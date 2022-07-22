use crate::util::screen;
use crate::util::screen_center;
use face_detect::FaceDetector;
use opencv::{
    core::{Mat, Rect},
    prelude::{KalmanFilterTrait, MatTraitConst},
    video::KalmanFilter,
};
use std::error::Error;
use xcb::{
    x::{ConfigWindow, ConfigureWindow, Drawable, GetGeometry, Window},
    Connection,
};

pub struct Throttler<T: Copy> {
    skips: u8,
    skip_rate: u8,
    prev: T,
}
impl<T: Copy> Throttler<T> {
    pub fn new(skip_rate: u8, default: T) -> Self {
        Throttler {
            skips: 0,
            skip_rate: skip_rate,
            prev: default,
        }
    }
    fn throttle<F: FnMut() -> T>(&mut self, mut func: F) -> T {
        if self.skips % self.skip_rate == 0 {
            self.skips = 1;
            self.prev = func();
            return self.prev;
        } else {
            self.skips += 1;
            return self.prev;
        }
    }
}

pub fn pan_window(
    connection: &Connection,
    window: Window,
    delta: (i32, i32),
) -> Result<(), Box<dyn Error>> {
    let cookie = connection.send_request(&GetGeometry {
        drawable: Drawable::Window(window),
    });
    let reply = connection.wait_for_reply(cookie).unwrap();

    connection.send_request(&ConfigureWindow {
        window: window,
        value_list: &[
            ConfigWindow::X(
                screen_center(&connection).unwrap().0 as i32 + delta.0 - reply.width() as i32 / 2,
            ),
            ConfigWindow::Y(
                screen_center(&connection).unwrap().1 as i32 + delta.1 - reply.height() as i32 / 2,
            ),
        ],
    });
    Ok(())
}
pub fn pan_desktop(
    connection: &Connection,
    frame: &Mat,
    face_detector: &mut FaceDetector,
    windows: &Vec<Window>,
    kalman_filter: &mut KalmanFilter,
    throttler: &mut Throttler<Rect>,
) -> Result<(), Box<dyn Error>> {
    let frame_center = (frame.cols() / 2, frame.rows() / 2);

    let face_rectangle = face_detector.detect_face(frame).unwrap();  // throttler.throttle(move || {face_detector.detect_face(frame).unwrap()});

    let screen_width = screen(&connection).unwrap().width_in_pixels();
    let screen_height = screen(&connection).unwrap().height_in_pixels();
    let screen_center_ = screen_center(connection).unwrap();
    if face_rectangle.x >= 0
        && face_rectangle.y >= 0
        && face_rectangle.x + face_rectangle.width <= screen_width as i32
        && face_rectangle.y + face_rectangle.height <= screen_height as i32
    {
        let mut face_center = (
            face_rectangle.x + face_rectangle.width / 2,
            face_rectangle.y + face_rectangle.height / 2,
        );
        let mut face_delta = (face_center.0 - frame_center.0, face_center.1 - frame_center.1);
        face_center = (screen_center_.0 as i32 + face_delta.0 * 4, screen_center_.1 as i32 + face_delta.1 * 4);

        kalman_filter.predict(&Mat::default()).unwrap();
        let face_center_arr: [[f64; 1]; 2] = [[face_center.0 as f64], [face_center.1 as f64]];
        let face_center_mat = Mat::from_slice_2d(&face_center_arr).unwrap();
        let face_center_corrected = kalman_filter.correct(&face_center_mat).unwrap();

        face_center = (
            *face_center_corrected.at::<f64>(0).unwrap() as i32,
            *face_center_corrected.at::<f64>(3).unwrap() as i32,
        );
        face_delta = (face_center.0 - frame_center.0, -face_center.1 + frame_center.1);

        for window in windows {
            pan_window(connection, *window, face_delta).unwrap();
        }
    }
    Ok(())
}
