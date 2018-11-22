import React from "react";
import PropTypes from "prop-types";

import SearchResult from "./SearchResult";

class SearchScan extends React.Component {
  constructor(props) {
    super(props);

    const { queryId, querySequence, results } = props || {};
    this.queryId = queryId;
    this.querySequence = querySequence;
    this.results = results || [];

    if (results && results.length) {
      this.results = results.map(resultData => new SearchResult(resultData));
    }
  }

  render() {
    return null;
  }
}

SearchScan.propTypes = {
  queryId: PropTypes.string.isRequired,
  querySequence: PropTypes.string.isRequired,
  results: PropTypes.array.isRequired
};

function assertPyObject(data, objNameExpected) {
  let error = null;
  if (typeof data !== "object") {
    error = `data is not an object: ${JSON.stringify(data)}`;
  } else {
    const objName = data["py/object"];
    if (typeof objName === "undefined") {
      error = `data does not have 'py/object' field: ${JSON.stringify(data)}`;
    } else if (objName !== objNameExpected) {
      error = `wrong py/object (expected ${objNameExpected}, got ${objName})`;
    }
  }
  if (error) {
    throw Error(`assertPyObject failed: ${error}`);
  }
  return true;
}

function parseFasta(fasta) {
  const lines = fasta.split("\n");
  if (!lines[0].startsWith(">")) {
    throw Error(
      `failed to parse fasta (header line does not start with '>'): ${lines[0]}`
    );
  }
  const id = lines.shift().substr(1);
  const seq = lines.map(line => line.trim()).join("");
  return { id, seq };
}

function parseCathScanResponseData(data) {
  assertPyObject(data, "cathpy.funfhmmer.ResultResponse");
  // console.log("response: ", data);
  console.log(
    "data: ",
    JSON.stringify(data).substr(0, 200),
    "---8<---",
    JSON.stringify(data).substr(-200)
  );
  const query = parseFasta(data["query_fasta"]);
  const scanData = data.funfam_scan;
  assertPyObject(scanData, "cathpy.models.Scan");
  const results = scanData.results ? scanData.results : [];
  const scanArgs = {
    queryId: query.id,
    querySequence: query.seq,
    featureCols: data.featureCols,
    results: results.map(result => {
      assertPyObject(result, "cathpy.models.ScanResult");
      // console.log("result: ", JSON.stringify(result).substr(0, 200));
      const hits = result.hits ? result.hits : [];
      return {
        queryId: result.query_id,
        queryLength: result.query_length,
        hits: hits.map(hit => {
          // console.log("hit: ", hit);
          assertPyObject(hit, "cathpy.models.ScanHit");
          const hsps = hit.hsps ? hit.hsps : [];
          const hitData = hit["data"] ? hit["data"] : {};
          return {
            matchId: hit.match_name,
            matchLength: hit.match_length,
            matchDescription: hit.match_description,
            matchSuperfamilyId: hit.match_cath_id
              ? hit.match_cath_id.id
              : undefined,
            significance: hit.significance,
            matchEcCount: hitData.ec_term_count,
            matchGoCount: hitData.go_term_count,
            matchFunfamMembers: hitData.funfam_members,
            repSourceId: hitData.rep_source_id,
            hsps: hsps.map(hsp => {
              assertPyObject(hsp, "cathpy.models.ScanHsp");
              // console.log("hsp: ", hsp);
              return {
                queryStart: hsp.query_start,
                queryEnd: hsp.query_end,
                matchStart: hsp.hit_start,
                matchEnd: hsp.hit_end
              };
            })
          };
        })
      };
    })
  };
  // console.log("scanArgs: ", scanArgs, SearchScan);
  const scan = new SearchScan(scanArgs);
  return scan;
}

export { parseCathScanResponseData };
export default SearchScan;
