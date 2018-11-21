import React from 'react';
import PropTypes from "prop-types";
import SearchHit from './SearchHit';

class SearchResult extends React.Component {

  propTypes = {
    queryId: PropTypes.string.isRequired,
    queryLength: PropTypes.string.isRequired,
    hits: PropTypes.array.isRequired,
  };

  defaultProps = {
    hits: [],
  };

  constructor(props) {
    super(props);

    console.log("SearchResults.new", props);

    const { queryId, queryLength, hits } = props;
    this.queryId = queryId;
    this.queryLength = queryLength;
    this.hits = hits;
    if ( hits.length ) {
      this.hits = hits.map(hitData => new SearchHit(hitData));
    }
  }
}

export default SearchResult;