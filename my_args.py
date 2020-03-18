import os
import datetime
import argparse
import numpy
import networks
import  torch
modelnames =  networks.__all__
# import datasets
datasetNames = ('Vimeo_90K_interp', 'Pixel_art_interp') #datasets.__all__

parser = argparse.ArgumentParser(description='DAIN')

'''공용
'''
parser.add_argument('--debug',action = 'store_true', help='Enable debug mode')
# 새로운 모델을 추가할 수 있음. 현재는 networks/DAIN.py 사용
parser.add_argument('--netName', type=str, default='DAIN',
                    choices = modelnames,help = 'model architecture: ' +
                        ' | '.join(modelnames) +
                        ' (default: DAIN)')
# 처리할 채널 수. 일반적으로 그림은 RGB 이렇게 3개의 채널을 가짐
parser.add_argument('--channels', '-c', type=int,default=3,choices = [1,3], help ='channels of images (default:3)')
# 필터 크기가 클 수록 이미지에 대한 합성곱 처리를 적게 함. 이로 인해 이미지 세부가 잘 처리안될 수 있음
parser.add_argument('--filter_size', '-f', type=int, default=4, help = 'the size of filters used (default: 4)',
                    choices=[2,4,6, 5,51]
                    )
# 결과를 저장할 곳
parser.add_argument('--save_which', '-s', type=int, default=1, choices=[0,1], help='choose which result to save: 0 ==> interpolated, 1==> rectified')
# 0.5만 허용됨. 프레임 사이를 몇 장으로 보간할 지 결정함. 이걸 고치려면 DAIN 이해가 필수. network/DAIN.py:29
parser.add_argument('--time_step',  type=float, default=0.5, help='choose the time steps')
# CUDA 사용 여부
parser.add_argument('--use_cuda', default= True, type = bool, help='use cuda or not')

'''train.py 전용
'''
# 학습에 사용할 데이터
parser.add_argument('--datasetName', default=['Vimeo_90K_interp'],
                    choices= datasetNames,nargs='+',
                    help='dataset type : ' +
                        ' | '.join(datasetNames) +
                        ' (default: Vimeo_90K_interp)')
# 학습 데이터가 있는 경로
parser.add_argument('--datasetPath',default='', nargs='+', help = 'the path of selected datasets')
# 임의 값 생성을 위한 씨앗 값
parser.add_argument('--seed', type=int, default=1, help='random seed (default: 1)')
# 학습 반복 회수
parser.add_argument('--numEpoch', '-e', type = int, default=100, help= 'Number of epochs to train(default:150)')
# 학습 데이터에서 뽑아내는 데이터 단위
parser.add_argument('--batch_size', '-b',type = int ,default=1, help = 'batch size (default:1)' )
# 학습 데이터를 읽어들이는 프로세스 개수
parser.add_argument('--workers', '-w', type =int,default=8, help = 'parallel workers for loading training samples (default : 1.6*10 = 16)')
# 값의 변화에 대한 학습률. 값이 크면 정확도가 떨어지고 낮으면 처리 속도가 늘어난다.
parser.add_argument('--lr', type =float, default= 0.002, help= 'the basic learning rate for three subnetworks (default: 0.002)')
# ReLU와 관계 있는 듯...
parser.add_argument('--rectify_lr', type=float, default=0.001, help  = 'the learning rate for rectify/refine subnetworks (default: 0.001)')
# 흐름에 대한 학습율
parser.add_argument('--flow_lr_coe', type = float, default=0.01, help = 'relative learning rate w.r.t basic learning rate (default: 0.01)')
# 충돌에 대한 학습율
parser.add_argument('--occ_lr_coe', type = float, default=1.0, help = 'relative learning rate w.r.t basic learning rate (default: 1.0)')
# 필터에 대한 학습율
parser.add_argument('--filter_lr_coe', type = float, default=1.0, help = 'relative learning rate w.r.t basic learning rate (default: 1.0)')
# 문맥에 대한 학습율
parser.add_argument('--ctx_lr_coe', type = float, default=1.0, help = 'relative learning rate w.r.t basic learning rate (default: 1.0)')
# 깊이에 대한 학습율
parser.add_argument('--depth_lr_coe', type = float, default=0.001, help = 'relative learning rate w.r.t basic learning rate (default: 0.01)')
# parser.add_argument('--deblur_lr_coe', type = float, default=0.01, help = 'relative learning rate w.r.t basic learning rate (default: 0.01)')
parser.add_argument('--alpha', type=float,nargs='+', default=[0.0, 1.0], help= 'the ration of loss for interpolated and rectified result (default: [0.0, 1.0])')
parser.add_argument('--epsilon', type = float, default=1e-6, help = 'the epsilon for charbonier loss,etc (default: 1e-6)')
parser.add_argument('--weight_decay', type = float, default=0, help = 'the weight decay for whole network ' )
# 학습 중지로 판단되는 지점을 넘기기 위한 허용 회수
parser.add_argument('--patience', type=int, default=5, help = 'the patience of reduce on plateou')
# 학습 중지로 판단되는 지점을 넘기기 위한 값
parser.add_argument('--factor', type = float, default=0.2, help = 'the factor of reduce on plateou')
# 로그 등의 경로를 저장할 곳을 지정
parser.add_argument('--uid', type=str, default= None, help='unique id for the training')
# 경로가 이미 있으면 0~9까지의 값을 확장자 뒤에 설정해서 겹침을 피함
parser.add_argument('--force', action='store_true', help='force to override the given uid')

'''미사용
'''
# 데이터 중에서 훈련과 검증에 사용할 비율을 설정
parser.add_argument('--dataset_split', type = int, default=97, help = 'Split a dataset into trainining and validation by percentage (default: 97)')
parser.add_argument('--pretrained', dest='SAVED_MODEL', default=None, help ='path to the pretrained model weights')
parser.add_argument('--no-date', action='store_true', help='don\'t append date timestamp to folder' )
parser.add_argument('--use_cudnn',default=1,type=int, help = 'use cudnn or not')
parser.add_argument('--dtype', default=torch.cuda.FloatTensor, choices = [torch.cuda.FloatTensor,torch.FloatTensor],help = 'tensor data type ')
parser.add_argument('--single_output', default=False, help = 'unused and unknown')
parser.add_argument('--task', default='interp', help = 'unused and unknown')
# parser.add_argument('--resume', default='', type=str, help='path to latest checkpoint (default: none)')

args = parser.parse_args()

import shutil

if args.uid == None:
    unique_id = str(numpy.random.randint(0, 100000))
    print("revise the unique id to a random numer " + str(unique_id))
    args.uid = unique_id
    timestamp = datetime.datetime.now().strftime("%a-%b-%d-%H%M")
    save_path = './model_weights/'+ args.uid  +'-' + timestamp
else:
    save_path = './model_weights/'+ str(args.uid)

# print("no pth here : " + save_path + "/best"+".pth")
if not os.path.exists(save_path + "/best"+".pth"):
    # print("no pth here : " + save_path + "/best" + ".pth")
    os.makedirs(save_path,exist_ok=True)
else:
    if not args.force:
        raise("please use another uid ")
    else:
        print("override this uid" + args.uid)
        for m in range(1,10):
            if not os.path.exists(save_path+"/log.txt.bk" + str(m)):
                shutil.copy(save_path+"/log.txt", save_path+"/log.txt.bk"+str(m))
                shutil.copy(save_path+"/args.txt", save_path+"/args.txt.bk"+str(m))
                break



parser.add_argument('--save_path',default=save_path,help = 'the output dir of weights')
parser.add_argument('--log', default = save_path+'/log.txt', help = 'the log file in training')
parser.add_argument('--arg', default = save_path+'/args.txt', help = 'the args used')

args = parser.parse_args()


with open(args.log, 'w') as f:
    f.close()
with open(args.arg, 'w') as f:
    print(args)
    print(args,file=f)
    f.close()
if args.use_cudnn:
    print("cudnn is used")
    torch.backends.cudnn.benchmark = True  # to speed up the
else:
    print("cudnn is not used")
    torch.backends.cudnn.benchmark = False  # to speed up the

