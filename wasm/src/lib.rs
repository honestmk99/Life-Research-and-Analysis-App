use wasm_bindgen::prelude::*;
// use math;

#[wasm_bindgen]
extern {
    pub fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet(name: &str) {
    alert(&format!("Hello, {}!", name));
}


fn diffc(v: f64, c: f64, diff: f64) -> f64 {
    return (v - c) / 6.0 / diff + 0.5;
}

// RGB: 255, 255, 255
// HSV: 360, 100, 100
pub fn rgb2hsv(arr: &[usize; 3]) -> [usize; 3] {
    let r = arr[0] as f64;
    let g = arr[1] as f64;
    let b = arr[2] as f64;
    let r = r / 255.0;
    let g = g / 255.0;
    let b = b / 255.0;

    // let v = Math.max(r, g, b);
    let v = f64::max(f64::max(r, g), b);
    let min = f64::min(f64::min(r, g), b);
    let diff = v - min;
  
    let mut h: f64 = 0.0;
    let mut s: f64 = 0.0;
    if diff != 0.0 {
        s = diff / v;
        let rr = diffc(v, r, diff);
        let gg = diffc(v, g, diff);
        let bb = diffc(v, b, diff);
    
        if r == v {
            h = bb - gg;
        } else if g == v {
            h = 1.0 / 3.0 + rr - bb;
        } else if b == v {
            h = 2.0 / 3.0 + gg - rr;
        }

        if h < 0.0 {
            h += 1.0;
        } else if h > 1.0 {
            h -= 1.0;
        }
    }
    [math::round::half_down(h * 360.0, 0) as usize, 
    math::round::half_down(s * 100.0, 0) as usize,
    math::round::half_down(v * 100.0, 0) as usize]
}

// RGB: 255, 255, 255
// HSV: 360, 100, 100
pub fn hsv2rgb(hsv: &[usize; 3]) -> [usize; 3] {
    let _l = hsv[0] as f64;
    let _m = hsv[1] as f64;
    let _n = hsv[2] as f64;
    let mut new_r: f64;
    let mut new_g: f64;
    let mut new_b: f64;

    if _m == 0.0 {
        new_r = math::round::half_down((255.0 * _n) / 100.0, 0);
        new_g = new_r;
        new_b = new_r;
    } else {
      let _m = _m / 100.0;
      let _n = _n / 100.0;

      let p = math::round::half_down(_l / 60.0, 0) % 6.0;
      let f = _l / 60.0 - (p as f64);
      let a = _n * (1.0 - _m);
      let b = _n * (1.0 - _m * f);
      let c = _n * (1.0 - _m * (1.0 - f));

      let pint = p as isize;
      match pint {
        0 => {
            new_r = _n;
            new_g = c;
            new_b = a;
        }
        1 => {
            new_r = b;
            new_g = _n;
            new_b = a;
        }
        2 => {
            new_r = a;
            new_g = _n;
            new_b = c;
        }
        3 => {
            new_r = a;
            new_g = b;
            new_b = _n;
        }
        4 => {
            new_r = c;
            new_g = a;
            new_b = _n;
        }
        5 => {
            new_r = _n;
            new_g = a;
            new_b = b;
        }
        _ => {
            new_r = 0.0;
            new_g = 0.0;
            new_b = 0.0;
        }
      }
      new_r = math::round::half_down(255.0 * new_r, 0);
      new_g = math::round::half_down(255.0 * new_g, 0);
      new_b = math::round::half_down(255.0 * new_b, 0);
    }
    return [new_r as usize, new_g as usize, new_b as usize];
}

#[wasm_bindgen]
pub fn change_image_luminance(data: Vec<usize>, scale: f64) -> Vec<usize> {
    let mut i: usize = 0;
    let mut rs = Vec::new();
    while i < data.len() {
        let mut hsv = rgb2hsv(&[data[i], data[i + 1], data[i + 2]]);
        hsv[2] = math::round::half_down( (hsv[2] as f64) * (1.0 + scale), 0) as usize;
        let rgb = hsv2rgb(&[hsv[0], hsv[1], hsv[2]]);

        rs.push(rgb[0]);
        rs.push(rgb[1]);
        rs.push(rgb[2]);
        rs.push(data[i + 3]);

        // data[i] = rgb[0];
        // data[i + 1] = rgb[1];
        // data[i + 2] = rgb[2];  

        i += 4;
    }    
    return rs;
}

#[wasm_bindgen]
pub fn balance_lighting(data: Vec<usize>) -> Vec<usize> {
    let mut rs = Vec::new();

    let mut hsv_data: Vec<[usize; 3]> = Vec::new();

    let mut brightness_total = 0;

    let mut pix_pos: usize = 0;
    while pix_pos < data.len() {
        let hsv = rgb2hsv(&[data[pix_pos], data[pix_pos + 1], data[pix_pos + 2]]);
        brightness_total += hsv[2];
        hsv_data.push(hsv);

        pix_pos += 4;
    }
  
    if hsv_data.len() == 0 {return data};

    let threholdavg = (brightness_total as f64) / (hsv_data.len() as f64);
    let threhold_fix = 81.0;

    let thredhold = math::round::half_down((threholdavg + threhold_fix) / 2.0, 0) as usize;
  
    for (idx, hsv) in hsv_data.iter().enumerate() {
        if hsv[2] > thredhold {
            let new_rgb = hsv2rgb(&[hsv[0], hsv[1], thredhold]);
            rs.push(new_rgb[0]);
            rs.push(new_rgb[1]);
            rs.push(new_rgb[2]);    
        } else {
            rs.push(data[idx * 4]);
            rs.push(data[idx * 4 + 1]);
            rs.push(data[idx * 4 + 2]);
        }

        rs.push(255);
    }
    return rs;
}

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_rgb2hsv() {
        assert_eq!(rgb2hsv(&[160, 72, 220]), [276, 67, 86]);
    }

    #[test]
    fn test_hsv2rgb() {
        assert_eq!(hsv2rgb(&[276, 67, 86]), [160, 72, 219]);
    }
}
