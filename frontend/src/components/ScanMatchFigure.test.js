import React from "react";
import { shallow } from "enzyme";
import ScanMatchFigure from "./ScanMatchFigure";
import { parseCathScanResponseData } from "../models/SearchScan";
import testScanJson from "../models/test_data/CathScanResults.test.json";

describe("ScanMatchFigure", () => {
  let props;

  beforeEach(() => {
    const testScanData = JSON.parse(testScanJson.results_json);
    const testScan = parseCathScanResponseData(testScanData);
    const testScanLength = testScan.querySequence.length;
    const testScanSegments = testScan.results[0].hits[0].hsps.map(
      (hsp, idx) => {
        return { id: idx, start: hsp.queryStart, end: hsp.queryEnd };
      }
    );
    props = {
      residueLength: testScanLength,
      segments: testScanSegments,
      width: 200
    };
  });

  // All tests will go here

  it("create new okay", () => {
    const wrapper = shallow(<ScanMatchFigure {...props} />)
    const scanMatch = wrapper.find(ScanMatchFigure)
    console.log("wrapper", wrapper);
    console.log("scanMatch", scanMatch);
    expect(scanMatch).equals(ScanMatchFigure);
  });
});
