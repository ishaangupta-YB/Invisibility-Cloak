import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import asyncio
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer


class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.background_captured = False
        self.background = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = np.flip(img, axis=1)

        if not self.background_captured:
            self.capture_background(img)
            self.background_captured = True

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask1 = mask1 + mask2

        mask1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
        mask1 = cv2.morphologyEx(mask1, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)

        mask2 = cv2.bitwise_not(mask1)

        res1 = cv2.bitwise_and(self.background, self.background, mask=mask1)
        res2 = cv2.bitwise_and(img, img, mask=mask2)

        final_output = cv2.addWeighted(res1, 1, res2, 1, 0)

        return final_output

    def capture_background(self, img):
        st.text("Capturing background frames. Do not move for a few seconds...")

        for _ in range(30):
            temp_background = img
            if self.background is None:
                self.background = temp_background
            else:
                self.background = cv2.addWeighted(self.background, 0.5, self.background, 0.5, 0)
        self.background_captured = True

        st.success("Background captured successfully!")


async def main():
    st.title("Harry Potter Invisibility Cloak")

    embed_component = {'linkedin': """<script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
            <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="medium" data-theme="light" data-type="VERTICAL" data-vanity="ishaangupta1201" data-version="v1"><a class="badge-base__link LI-simple-link" href="https://in.linkedin.com/in/ishaangupta1201?trk=profile-badge"></a></div>"""}
    with st.sidebar:
        st.sidebar.title("Author")
        components.html(embed_component['linkedin'],height=310)

    webrtc_ctx = webrtc_streamer(key="example", video_processor_factory=VideoTransformer)

    if not webrtc_ctx.state.playing:
        print('WebRTC not connected')

    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())


