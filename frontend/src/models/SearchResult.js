import React from "react";
import PropTypes from "prop-types";
import SearchHit from "./SearchHit";

export class SearchResult extends React.Component {
  constructor(props) {
    super(props);

    const { queryId, queryLength, hits } = props;
    this.queryId = queryId;
    this.queryLength = queryLength;
    this.hits = hits;
    if (hits.length) {
      this.hits = hits.map(hitData => new SearchHit(hitData));
    }
  }
}

SearchResult.defaultProps = {
  hits: []
};

SearchResult.propTypes = {
  queryId: PropTypes.string.isRequired,
  queryLength: PropTypes.string.isRequired,
  hits: PropTypes.array.isRequired
};

export default SearchResult;
