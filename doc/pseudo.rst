+----------------------------------------------+--------------------------+
| Step                                         | Actor                    |
+==============================================+==========================+
| 1. Open csv file as connection               | reader.open_csv()        |
+----------------------------------------------+--------------------------+
| 2. Convert file to list of Rows instances    |                          |
+----------------------------------------------+                          |
| 3. Split list to segments and                |                          |
|    get parsing definition for each segment   | reader.Reader().items()  |
+----------------------------------------------+                          |
| 4. Supply segment and a parsing definition   |                          |
|    for further processing                    |                          |
+----------------------------------------------+--------------------------+
| 5. Group rows to tables                      |                          |
|                                              | parcer.extract_tables()  |
+----------------------------------------------+                          |
| 6. Extract variable name and unit of         |                          |
|    measurement from each table               |                          |
+----------------------------------------------+                          |
| 7. Filter defined tables and check all       |                          |
|    required variables were read              |                          |
+----------------------------------------------+--------------------------+
| 8. Submit tables to an emitter instance      |                          |
+----------------------------------------------+                          |
| 9. Import datapoints from table datarows     | emitter.Emitter()        |
|    by frequency                              |                          |
+----------------------------------------------+                          |
| 10. Create dataframes by frequency           |                          |
+----------------------------------------------+--------------------------+
| 11. Save dataframes in csv files             | Vintage().save()         |
+----------------------------------------------+--------------------------+
