class NumericalComputer:
    def __init__(self, **kwargs) -> None:
        self.plot = kwargs.get("plot", False)
        self.dry_run = kwargs.get("dry_run", False)

    def compute(self, **kwargs):
        raise NotImplementedError("Method compute not implemented")