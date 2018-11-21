import React from 'react';
import PropTypes from 'prop-types';

class SearchHsp extends React.Component {

  propTypes = {
    queryStart: PropTypes.string.isRequired,
    queryEnd: PropTypes.string.isRequired,
    matchStart: PropTypes.string.isRequired,
    matchEnd: PropTypes.string.isRequired,
  };

  constructor(props) {
    super();

    const { queryStart, queryEnd, matchStart, matchEnd } = props;
    this.queryStart = queryStart;
    this.queryEnd   = queryEnd;
    this.matchStart = matchStart;
    this.matchEnd   = matchEnd;
  }
  render() { return null }
}

export default SearchHsp;
