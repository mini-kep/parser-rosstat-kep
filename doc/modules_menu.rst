:doc:`csv2df.helpers`. 
    File and folder locations for interim and processed CSV files.
    
    Functions based on :class:`csv2df.files.Folder` class methods:
    
        - :func:`csv2df.files.get_latest_date` returns latest available
          year and month
        - :func:`csv2df.files.locate_csv` retrieves interim CSV file for parsing
          from *data/interim* folder by year and month
        - based on year and month :func:`csv2df.files.get_processed_folder` provides
          location to save parsing result in *data/processed* folder
    
    
    For housekeeping :mod:`csv2df.files` provides:
    
     - :func:`csv2df.files.init_dirs` - make directory structure on startup
     - :func:`csv2df.files.copy_latest` - copy CSVs to *latest* folder which
       has stable URL
    
    
    For reference - data directory structure::
    
        \data
          \interim
              \2017
              \2016
              \...
          \processed
              \latest
              \2017
              \2016
              \...
    
:doc:`csv2df.specification`. 
    :mod:`csv2df.spec` module contains data structures used as parsing instructions.
    
    Global variable  **SPEC** (:class:`csv2df.spec.Specification`) allows access to
    parsing definitions:
    
      - :func:`csv2df.spec.Specification.get_main_parsing_definition` retrieves
        main (default) parsing definition, where most indicators are defined;
    
      - :func:`csv2df.spec.Specification.get_segment_parsing_definitions` provides
        a list of parsing defintions by csv segment.
    
    We parse CSV file by segment, because some table headers repeat themselves in
    CSV file. Extracting a piece out of CSV file gives a good isolated input for
    parsing.
    
    Previously **SPEC** was initialised from yaml file, but this led to many errors,
    so the parsing instructions are now created internally in *spec.py*.
    
    **SPEC** is used by:
    
      - :class:`csv2df.rows.RowStack`
      - :func:`csv2df.tables.extract_tables`
    
    
:doc:`csv2df.reader`. 
    Read CSV file and represent it as a list of Row class instances.
:doc:`csv2df.parcer`. 
    Parse [(csv_segment, pdef)... ] inputs into Table() instances using
       parsing specification.
    
    Main call:
       tables = get_tables(rows, SPEC)
    
    
:doc:`csv2df.runner`. 
    Get pandas dataframes for a given data and month. 
    
    *get_dataframes(csvfile, spec=SPEC)* is a lower-level function to get 
    dataframes from *csvfile* connection under *spec* parsing instruction.  
    
    *Vintage* class addresses dataset by year and month:
    
        Vintage(year, month).save()
        Vintage(year, month).validate()
    
    These calls should give similar results:
        
        csv_path = PathHelper.locate_csv(year, month)
        csvfile = open_csv(csv_path)
        
        Vintage(year, month).dfs()
    
    *Collection* manipulates all datasets, released at various dates:
    
        Collection.save_all()
        Collection.save_latest()
        Collection.approve_latest()
        Collection.approve_all()
    
:doc:`csv2df.validator`. 
    Use hardcoded constants for year 1999 to validate dfa, dfq, dfm dataframes.
       These dataframes are the result of parsign procedure.
    
       Hardcoded constants are recorded in ANNUAL, QTR and MONTHLY variables,
       converted to dictionaries using *serialise()*. CHECKPOINTS holds all
       sample datapoints as dictionaries.
    
       Validator(dfa, dfq, dfm).run() tests dataframes against CHECKPOINTS.
    
    
    
:doc:`csv2df.util_label`. 
    Variable labels.
    
    Used to handle strings like GDP_rog, GOV_EXPENSE_bln_rub and its parts.
    
    
:doc:`csv2df.util_row_splitter`. 
    Splitter functions extract annual, quarterly and monthly values from data row.
