import React from "react";
import { mount } from "enzyme";
import ScanMatchFigure from "./ScanMatchFigure";
import { parseCathScanResponseData } from "../models/SearchScan";
import testScanJson from "../models/test_data/CathScanResults.test.json";

describe("ScanMatchFigure", () => {
  let props;
  let mountedScanMatchFigure;

  const scanMatchFigure = () => {
    if (!mountedScanMatchFigure) {
      mountedScanMatchFigure = mount(<ScanMatchFigure {...props} />);
    }
    return mountedScanMatchFigure;
  };

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
    mountedScanMatchFigure = undefined;
  });

  // All tests will go here

  it("create new okay", () => {
    const scanMatch = scanMatchFigure();
    console.log("scanMatch", scanMatch);
    expect(scanMatch).toBeInstanceOf(ScanMatchFigure);
  });
});
