import React from "react";
import PropTypes from "prop-types";

import SearchResult from './SearchResult';

class SearchScan extends React.Component {

  propTypes = {
    queryId: PropTypes.string.isRequired,
    querySequence: PropTypes.string.isRequired,
    renderMatchId: PropTypes.func.isRequired,
    featureCols: PropTypes.func.isRequired,
    results: PropTypes.array.isRequired,
  };

  defaultProps = {
    results: [],
  };

  constructor(props) {
    super();

    const { queryId, querySequence, renderMatchId, featureCols, results } = props;
    this.queryId = queryId;
    this.querySequence = querySequence;
    this.renderMatchId = renderMatchId;
    this.featureCols = featureCols;
    this.results = results;

    if ( results.length ) {
      this.results = results.map(resultData => new SearchResult( resultData ));
    }
  }

  render() { return null }

}

export function parseCathScanData(data) {
  const scan = {
    featureCols: data.featureCols,
    results: data.results.map( result => {
      return {
        queryId: result.query_id,
        queryLength: result.query_length,
        hits: result.hits.map( hit => {
          return {
            matchId: hit.match_id,
            matchLength: hit.match_length,
            matchDescription: hit.match_description,
            matchSuperfamilyId: hit.match_superfamily_id,
            significance: hit.significance,
            matchEcCount: hit.ec_term_count,
            matchGoCount: hit.go_term_count,
            matchFunfamMembers: hit.funfam_members,
            repSourceId: hit.rep_source_id,
            hsps: hit.hsps.map( hsp => {
              return {
                queryStart: hsp.query_start,
                queryEnd: hsp.query_end,
                matchStart: hsp.match_start,
                matchEnd: hsp.match_end,
              }
            }),
          }
        }),
      }
    }),
  };
  return new SearchScan(scan);
}

export default SearchScan;