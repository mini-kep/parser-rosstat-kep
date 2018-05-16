
#FIXME: validation is ugly 
from kep.validation.checkpoints import (
    CHECKPOINTS,
    OPTIONAL_CHECKPOINTS,
    validate2
)

#FIXME: validation is ugly 
def validate(dfs):
    for freq in FREQUENCIES:
        validate2(df=dfs[freq],
                  required_checkpoints=CHECKPOINTS[freq],
                  additional_checkpoints=OPTIONAL_CHECKPOINTS[freq],
                  strict=False)
    print("Test values parsed OK for")



# FIXME: too many responsibilities
from kep.helper.date import Date

class Latest(Vintage):
    """Operations on most recent data release."""

    def __init__(self, year: int, month: int):
        # protect from using old releases of data
        Date(year, month).assert_latest()
        super().__init__(year, month)

    def upload(self):
        from parsers.mover.uploader import Uploader
        self.validate()
        # FIXME: possible risk - *self.datapoints* may have different serialisation 
        #        format compared to what Uploader() expects
        #           (a) date format   
        #           (b) extra keys in dictionary
        Uploader(self.datapoints).post()

    def save(self, folder=None):
        ProcessedCSV(self.year, self.month).to_latest()


if __name__ == "__main__": # pragma: no cover
    v = Vintage(2018, 1)
    validate(v.dfs)
    v.save()