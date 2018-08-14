"""Check datapoints with control values."""

class ValidationError(Exception):
    pass        
  
def require_any(checkpoints, datapoints):   
    found = [c for c in checkpoints if c in datapoints]
    if not found:
        raise ValidationError(f'Found none of: {checkpoints}')
    return found    

def require_all(checkpoints, datapoints):   
    for x in checkpoints:
        if x not in datapoints:
            raise ValidationError(f'Required value not found: {x}')
    return checkpoints             

def validate(datapoints, checkpoints, optional_lists):
    """Check datapoints with control values found in YAML file at *filepath*.
       Raise ValidationError on error.
    """
    require_all(checkpoints, datapoints)
    for _checkpoints in optional_lists:
        require_any(_checkpoints, datapoints)
    # TODO: show how many of time series are covered     
    print("All values checked")  