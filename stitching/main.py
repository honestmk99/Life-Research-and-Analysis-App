import time
from pathlib import Path
from typing import List, Dict
import json

from celery_tasks.tasks import StitchingCeleryTask
from celery_tasks.utils import create_worker_from

from ashlar import filepattern
from ashlar import reg


def ashlar_stitch(tiles, pattern):
    """
    Stitches tiles using the Ashlar library.

    Separate function for testing purposes
    """

    # deserialize list of json strings
    tiles = [json.loads(t) for t in tiles]

    tile_folder = Path(tiles[0].get("absolute_path")).parent

    reader = filepattern.FilePatternReader(path=str(tile_folder),
                                           pattern=pattern, overlap=0.2)
    start = time.perf_counter()
    # perform actual alignment
    aligner = reg.EdgeAligner(reader, channel=0, filter_sigma=10, max_shift=500, verbose=True,
                              do_make_thumbnail=True, permutations_multiplier=1)
    # aligner = reg.EdgeAligner(reader, channel=0, filter_sigma=10, verbose=True, do_make_thumbnail=True)
    aligner.run()

    print(f"EdgeAligner took: {time.perf_counter() - start: 0.4f} seconds")

    # generate stitched file
    start = time.perf_counter()

    out_file_format = "stitched_{channel}.tif"

    mosaic = reg.Mosaic(
        aligner=aligner,
        shape=aligner.mosaic_shape,
        filename_format=out_file_format
    )

    # output result to array in python -> need to perform cropping
    merged = mosaic.run(mode='return')
    merged = mosaic.run(mode='write')
    print(f"mosaic took: {time.perf_counter() - start: 0.4f} seconds")

    # merged_array = np.array(merged)

    return {'foo': 123}


class StitchingCeleryTaskImpl(StitchingCeleryTask):

    def run(self, tiles, pattern):
        return ashlar_stitch(tiles, pattern)


# create celery app
app, _ = create_worker_from(StitchingCeleryTaskImpl)

# start worker
if __name__ == '__main__':
    # time.sleep(30)
    app.worker_main()
