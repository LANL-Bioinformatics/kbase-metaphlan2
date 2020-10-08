/*
A KBase module: metaphlan2
*/

module metaphlan2 {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_metaphlan2(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef exec_metaphlan(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
