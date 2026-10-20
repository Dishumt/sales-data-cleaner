import pytest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from project import get_file, clean_data, report

#1. TESTING get_file()
#========================================================================================================================================+

def test_get_file(monkeypatch, tmp_path):
#check wether get_file() reads intended file properly
    test_filename = tmp_path / "test_data.csv"

    df_fake = pd.DataFrame({"Invoice": [489434], "StockCode": [85048], "Quantity": [1], "Price": [1.0]})
    df_fake.to_csv(test_filename, index=False)

    monkeypatch.setattr("sys.argv", ["project.py", str(test_filename)])
    df = get_file()
    assert not df.empty

#check wether get_file() handles file with unintended extention properly
    monkeypatch.setattr("sys.argv", ["project.py", "data.txt"])
    
    with pytest.raises(SystemExit) as exc_info:
        get_file()
        
    assert exc_info.value.code == "Usage: python project.py <filename.csv>"
#check wether get_file() handles file with unintended sys.argv properly
    monkeypatch.setattr("sys.argv", ["project.py"])

    with pytest.raises(SystemExit) as exc_info:
            get_file()
            
    assert exc_info.value.code == "Usage: python project.py <filename.csv>"

#check wether get_file() handles csv-file missing critical columns properly
    required_headers = ["Invoice", "StockCode", "Quantity", "Price"]
    test_filename = tmp_path / "test_data.csv"

    df_fake = pd.DataFrame({"StockCode": [85048], "Quantity": [1], "Price": [1.0]}) #critical column "Invoice" missing
    df_fake.to_csv(test_filename, index=False)

    monkeypatch.setattr("sys.argv", ["project.py", str(test_filename)])
    with pytest.raises(SystemExit) as exc_info:
            get_file()
    
    assert exc_info.value.code == f"The table must contain required headers: {', '.join(required_headers)}"
#====================================================================================================================================+
#2 TESTING clean_data(df)

def test_clean_data(monkeypatch,tmp_path):
#checking whether clean_data(df) works properly with intended data 
     test_filename = tmp_path / "test_data.csv"
     
     df_fake = pd.DataFrame({"Invoice": ["C489434",np.nan,"489434"],
                             "StockCode": [85048,85049,85050],
                             "Description": ["Item1",np.nan,"Item3"],
                             "Quantity": [-1,2,3],
                             "Price": [1.0,1.2,1.4]})
     df_fake.to_csv(test_filename, index=False)

     removed_expected = pd.DataFrame({"Invoice": ["C489434",np.nan],
                                      "StockCode": [85048,85049],
                                      "Description": ["Item1","Unknown"],
                                      "Quantity": [-1,2],
                                      "Price": [1.0,1.2],
                                      "Removal reason": ["Anomal_quantity; Canceled_operation;", "Invoice_missing;",]
                                      })

     cleaned_expected = pd.DataFrame({"Invoice": ["489434"],
                                      "StockCode": [85050],
                                      "Description": ["Item3"],
                                      "Quantity": [3],
                                      "Price": [1.4]})


     monkeypatch.setattr("sys.argv", ["project.py", str(test_filename)])
     df = get_file()
     removed,cleaned = clean_data(df)
     assert_frame_equal(removed.reset_index(drop=True),removed_expected.reset_index(drop=True))
     assert_frame_equal(cleaned.reset_index(drop=True),cleaned_expected.reset_index(drop=True))
 #==============================================================================================================================+
#3 TESTING report(df, removed, cleaned)

#checking whether the function avoids zero division
def test_report(monkeypatch, tmp_path):
    test_filename = tmp_path / "test_data.csv"

    df_fake = pd.DataFrame({"Invoice": ["C489434","389434","489434"],
                            "StockCode": [85048,85049,85050],
                            "Description": ["Item1",np.nan,"Item3"],
                            "Quantity": [1,2,3],
                            "Price": [1.0,1.2,1.4]})
    df_fake.to_csv(test_filename, index=False)
    
    monkeypatch.setattr("sys.argv", ["project.py", str(test_filename)])
    df = get_file()
    removed,cleaned = clean_data(df)
    report(df, removed, cleaned)
#===============================================================================================================================+
