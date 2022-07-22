use num_traits::pow::Pow;
use opencv::{
    core::{Mat, CV_32F, CV_64F},
    prelude::{KalmanFilterTrait, KalmanFilterTraitConst, MatExprTraitConst},
    video::KalmanFilter,
};
pub fn kalman_init() -> KalmanFilter {
    let mut kalman_filter = KalmanFilter::new(6, 2, 0, CV_64F).unwrap();
    let dt = 0.1;
    let err_stdev = 1.0;
    let a = 64.0; // acceleration standard deviation
    let transition_matrix: [[f64; 6]; 6] = [
        [1.0, dt, 0.5 as f64 * dt.pow(2), 0.0, 0.0, 0.0],
        [0.0, 1.0, dt, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, dt, 0.5 as f64 * dt.pow(2)],
        [0.0, 0.0, 0.0, 0.0, 1.0, dt],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ];
    let state_pre: [[f64; 1]; 6] = [[0.0], [0.0], [0.0], [0.0], [0.0], [0.0]];
    let measurement_matrix: [[f64; 6]; 2] = [
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    ];
    let process_noise_cov: [[f64; 6]; 6] = [
        [
            a.pow(2) as f64 * dt.pow(4) as f64 / 4f64,
            a.pow(2) as f64 * dt.pow(3) as f64 / 2f64,
            a.pow(2) as f64 * dt.pow(2) / 2f64,
            0.0,
            0.0,
            0.0,
        ],
        [
            a.pow(2) as f64 * dt.pow(3) / 2f64,
            a.pow(2) as f64 * dt.pow(2),
            a.pow(2) as f64 * dt,
            0.0,
            0.0,
            0.0,
        ],
        [
            a.pow(2) as f64 * dt.pow(2) / 2 as f64,
            a.pow(2) as f64 * dt,
            a.pow(2) as f64 * 1.0,
            0.0,
            0.0,
            0.0,
        ],
        [
            0.0,
            0.0,
            0.0,
            a.pow(2) as f64 * dt.pow(4) as f64 / 4f64,
            a.pow(2) as f64 * dt.pow(3) / 2f64,
            a.pow(2) as f64 * dt.pow(2) / 2f64,
        ],
        [
            0.0,
            0.0,
            0.0,
            a.pow(2) as f64 * dt.pow(3) as f64 / 2f64,
            a.pow(2) as f64 * dt.pow(2),
            a.pow(2) as f64 * dt,
        ],
        [
            0.0,
            0.0,
            0.0,
            a.pow(2) as f64 * dt.pow(2) / 2f64,
            a.pow(2) as f64 * dt,
            a.pow(2) as f64 * 1.0,
        ],
    ];
    let measurement_noise_cov: [[f64; 2]; 2] = [
        [(err_stdev as f64).pow(2), 0.0],
        [0.0, (err_stdev as f64).pow(2)],
    ];
    kalman_filter.set_transition_matrix(Mat::from_slice_2d(&transition_matrix).unwrap());
    //kalman_filter.set_state_pre(Mat::from_slice_2d(&state_pre).unwrap());
    kalman_filter.set_measurement_matrix(Mat::from_slice_2d(&measurement_matrix).unwrap());
    kalman_filter.set_process_noise_cov(Mat::from_slice_2d(&process_noise_cov).unwrap());
    kalman_filter.set_measurement_noise_cov(Mat::from_slice_2d(&measurement_noise_cov).unwrap());

    kalman_filter
}
