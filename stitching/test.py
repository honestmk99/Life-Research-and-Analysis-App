import unittest


class TestStitching(unittest.TestCase):

    tiles = [
        {
            "_id": "61a4af8debd0ac97d6c2ff38",
            "user_id": "61a09650a0b429067a70ec97",
            "absolute_path": "/cache-storage/61a09650a0b429067a70ec97/tiles/img_r001_c001.tif",
            "file_name": "img_r001_c001.tif",
            "content_type": "image/tiff",
            "width_px": 1392,
            "height_px": 1040,
            "offset_x": 0,
            "offset_y": 0,
            "row_index": 0,
            "column_index": 0,
            "channel": "not specified"
        },
        {
            "_id": "61a4af8debd0ac97d6c2ff39",
            "user_id": "61a09650a0b429067a70ec97",
            "absolute_path": "/cache-storage/61a09650a0b429067a70ec97/tiles/img_r001_c002.tif",
            "file_name": "img_r001_c002.tif",
            "content_type": "image/tiff",
            "width_px": 1392,
            "height_px": 1040,
            "offset_x": 0,
            "offset_y": 0,
            "row_index": 0,
            "column_index": 0,
            "channel": "not specified"
        },
        {
            "_id": "61a4af8debd0ac97d6c2ff3a",
            "user_id": "61a09650a0b429067a70ec97",
            "absolute_path": "/cache-storage/61a09650a0b429067a70ec97/tiles/img_r001_c003.tif",
            "file_name": "img_r001_c003.tif",
            "content_type": "image/tiff",
            "width_px": 1392,
            "height_px": 1040,
            "offset_x": 0,
            "offset_y": 0,
            "row_index": 0,
            "column_index": 0,
            "channel": "not specified"
        }
    ]

    def test_stitch(self):
        pass

if __name__ == '__main__':
    unittest.main()