use ftwm::{event::handle_events, util::root, kalman_filter::kalman_init, panning::{pan_desktop, Throttler}};
use std::{error::Error};
use xcb::{x::ChangeWindowAttributes, Connection};
use opencv::{core::{Mat, Rect, Size}, videoio::{VideoCapture, CAP_ANY}, prelude::VideoCaptureTrait, highgui::{named_window, WINDOW_NORMAL, imshow, wait_key}, imgproc::{resize, INTER_LINEAR, INTER_AREA, cvt_color, COLOR_RGB2GRAY, COLOR_GRAY2RGB}};
use face_detect::FaceDetector;

fn register_wm(connection: &Connection) -> Result<(), Box<dyn Error>> {
    let mut flags = xcb::x::EventMask::empty();
    flags.insert(xcb::x::EventMask::PROPERTY_CHANGE);
    flags.insert(xcb::x::EventMask::STRUCTURE_NOTIFY);
    flags.insert(xcb::x::EventMask::SUBSTRUCTURE_NOTIFY);
    flags.insert(xcb::x::EventMask::SUBSTRUCTURE_REDIRECT);
    connection.send_request(&ChangeWindowAttributes {
        window: root(connection).unwrap(),
        value_list: &[xcb::x::Cw::EventMask(flags)],
    });
    Ok(())
}

fn main() { //-> Result<(), Box<dyn Error>> {
    let (connection, _screen) = Connection::connect(None).unwrap();
    let mut windows = Vec::new();
    let mut frame = Mat::default(); // Create an OpenCV matrix to store the frame.
    let mut video_capture = VideoCapture::new(0, CAP_ANY).expect("Couldn't open webcam."); // Create a new VideoCapture instance using CAP_ANY to auto-detect the backend.
    let mut face_detector = FaceDetector::new().unwrap();
    let mut kalman_filter = kalman_init();
    let mut throttler = Throttler::new(1, Rect {x: 0, y: 0, width: 0, height: 0});
    register_wm(&connection).unwrap();
    loop {
        video_capture
            .read(&mut frame)
            .expect("Couldn't get frame from webcam."); // Capture a frame and put it in the frame container.

        handle_events(&connection, &mut windows).unwrap();
        pan_desktop(
            &connection,
            &frame,
            &mut face_detector,
            &windows,
            &mut kalman_filter,
            &mut throttler,
        )
        .unwrap();

        connection.flush().unwrap();
    }
}
