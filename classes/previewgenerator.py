import cv2
import datetime
import os


class PreviewGenerator:

    def generate_preview(self, video_path, save_path) -> dict:
        print("[PreviewGenerator] Generating preview")
        start = datetime.datetime.now()

        # Open video
        cap = cv2.VideoCapture(video_path)

        # Get total frames
        tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print("Total frames:", tot_frames)

        # Get 9 frames in the video
        num_images = 9
        images = [self._get_frame(cap, i * int(tot_frames / num_images)) for i in range(num_images)]

        for i in images:
            print(type(i))

        '''
        images = []
        for i in range(num_images):
            #print(type(self._get_frame(cap, i * int(tot_frames / num_images+1))))
            import random as rnd
            print(type(self._get_frame(cap, rnd.randint(0, tot_frames))))
            exit()
        '''

        # Create 3 horizontal images
        h1 = cv2.hconcat(images[0:3])
        h2 = cv2.hconcat(images[3:6])
        h3 = cv2.hconcat(images[6:9])

        # Concat 3 full images
        #full_preview = np.concatenate((h1, h2, h3), axis=0)
        full_preview = cv2.vconcat([h1, h2, h3])

        print("[PreviewGenerator] Preview generated")

        # Save image
        preview_path = self._save_img(full_preview, save_path)

        diff_seconds = (datetime.datetime.now() - start).total_seconds()

        return {
            "path": preview_path,
            "seconds": diff_seconds
        }

    @staticmethod
    def _save_img(image, save_path):
        print("[PreviewGenerator] Saving preview in: {}".format(save_path))

        current_time = datetime.datetime.now()
        filename = current_time.strftime("%m%d%Y-%H%M%S.jpg")

        # Generate directory if not exists
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        full_path = os.path.join(save_path, filename)

        cv2.imwrite(full_path, image)
        print("[PreviewGenerator] Image saved")

        return full_path

    @staticmethod
    def _get_frame(cap, frame_num):
        print("n frame: ", frame_num)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()

        if frame is not None:
            scale_percent = 30  # percent of original size
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        else:
            return frame