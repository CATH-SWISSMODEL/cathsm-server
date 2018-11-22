import React from "react";
import { mount } from "enzyme";
import SearchScan, { parseCathScanResponseData } from "./SearchScan";

import test_scan_json from "./test_data/CathScanResults.test.json";

describe("SearchScan", () => {
  let props;
  let mountedSearchScan;
  const searchScan = () => {
    if (!mountedSearchScan) {
      mountedSearchScan = mount(<SearchScan {...props} />);
    }
    return mountedSearchScan;
  };

  beforeEach(() => {
    props = {
      queryId: undefined,
      querySequence: undefined,
      results: []
    };
    mountedSearchScan = undefined;
  });

  // All tests will go here

  it("create new okay", () => {
    const scan = new SearchScan();
    expect(scan).toBeDefined();
    expect(Array.isArray(scan.results)).toBeTruthy();
    expect(scan.results.length).toBe(0);
  });

  it("parseCathScanData returns SearchScan", () => {
    const results = JSON.parse(test_scan_json.results_json);
    const scan = parseCathScanResponseData(results);
    expect(scan).toBeInstanceOf(SearchScan);
  });
});
