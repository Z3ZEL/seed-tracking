class Record:
    def __init__(self, velocity : float, error_margin : float, plots : list[str], seed_images : list[str], main_seed_number : int, worker_seed_number : int, xz_gap : tuple[int], seed_id : str = None) -> None:
        self._velocity : float = velocity
        self._error_margin : float = error_margin
        self._plots : list[str] = plots
        self._seed_images : list[str] = seed_images
        self._main_seed_number : int = main_seed_number
        self._worker_seed_number : int = worker_seed_number
        self._seed_id : str = seed_id
        self._xz_gap : tuple[int] = xz_gap
        self._validated : bool = False

    def to_json(self) -> dict:
        ## Remove the validated key
        return {
            "velocity" : self._velocity,
            "error_margin" : self._error_margin,
            "plots" : self._plots,
            "seed_images" : self._seed_images,
            "seed_id" : self._seed_id,
            "worker_seed_number" : self._worker_seed_number,
            "main_seed_number" : self._main_seed_number,
            "xz_gap" : self._xz_gap
        }

    def to_csv_line(self) -> str:
        '''
            Return the record in csv format
        '''
        return f'{self._seed_id if self._seed_id else "no_id"},{self._velocity}, {self._error_margin}, {self._xz_gap[0]}, {self._xz_gap[1]}\n'