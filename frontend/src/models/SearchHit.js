import React from "react";
import PropTypes from "prop-types";
import SearchHsp from "./SearchHsp";

export class SearchHit extends React.Component {
  constructor(props) {
    super(props);

    this.matchId = props.matchId;
    this.matchDescription = props.matchDescription;
    this.matchLength = props.matchLength;
    this.matchSuperfamilyId = props.matchSuperfamilyId;
    this.significance = props.significance;
    this.matchEcCount = props.matchEcCount;
    this.matchGoCount = props.matchGoCount;
    this.matchFunfamMembers = props.matchFunfamMembers;
    this.repSourceId = props.repSourceId;

    this.hsps = props.hsps.map(hspData => new SearchHsp(hspData));
  }

  matchHasStructure = () => this.repSourceId === "cath";

  render() {
    return null;
  }
}

SearchHit.propTypes = {
  matchId: PropTypes.string.isRequired,
  matchDescription: PropTypes.string.isRequired,
  matchLength: PropTypes.string.isRequired,
  matchSuperfamilyId: PropTypes.string.isRequired,
  significance: PropTypes.number.isRequired,
  matchEcCount: PropTypes.string.isRequired,
  matchGoCount: PropTypes.string.isRequired,
  matchFunfamMembers: PropTypes.string.isRequired,
  repSourceId: PropTypes.string.isRequired
};

export default SearchHit;
