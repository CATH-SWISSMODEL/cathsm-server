import React from "react";
import PropTypes from "prop-types";

export class SearchHsp extends React.Component {
  constructor(props) {
    super(props);

    const { queryStart, queryEnd, matchStart, matchEnd } = props;
    this.queryStart = queryStart;
    this.queryEnd = queryEnd;
    this.matchStart = matchStart;
    this.matchEnd = matchEnd;
  }
  render() {
    return null;
  }
}

SearchHsp.propTypes = {
  queryStart: PropTypes.string.isRequired,
  queryEnd: PropTypes.string.isRequired,
  matchStart: PropTypes.string.isRequired,
  matchEnd: PropTypes.string.isRequired
};

export default SearchHsp;
