import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
import torch
from src.dataset.face_align.yoloface import YoloFace

class AlignImage(object):
    def __init__(self, device='cuda', det_path='checkpoints/yoloface_v5m.pt'):
        # Check if CUDA is available and compatible
        if device == 'cuda' and torch.cuda.is_available():
            try:
                # Test CUDA compatibility
                test_tensor = torch.tensor([1.0]).cuda()
                test_tensor = test_tensor.float()
                actual_device = device
            except RuntimeError as e:
                if "no kernel image is available" in str(e):
                    print("CUDA compatibility issue detected, using CPU for face detection")
                    actual_device = 'cpu'
                else:
                    raise e
        else:
            actual_device = 'cpu' if not torch.cuda.is_available() else device
            
        self.facedet = YoloFace(pt_path=det_path, confThreshold=0.5, nmsThreshold=0.45, device=actual_device)

    @torch.no_grad()
    def __call__(self, im, maxface=False):
        bboxes, kpss, scores = self.facedet.detect(im)
        face_num = bboxes.shape[0]

        five_pts_list = []
        scores_list = []
        bboxes_list = []
        for i in range(face_num):
            five_pts_list.append(kpss[i].reshape(5,2))
            scores_list.append(scores[i])
            bboxes_list.append(bboxes[i])

        if maxface and face_num>1:
            max_idx = 0
            max_area = (bboxes[0, 2])*(bboxes[0, 3])
            for i in range(1, face_num):
                area = (bboxes[i,2])*(bboxes[i,3])
                if area>max_area:
                    max_idx = i
            five_pts_list = [five_pts_list[max_idx]]
            scores_list = [scores_list[max_idx]]
            bboxes_list = [bboxes_list[max_idx]]

        return five_pts_list, scores_list, bboxes_list