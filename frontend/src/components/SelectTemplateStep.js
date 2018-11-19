import React, { Component } from "react";
import PropTypes from "prop-types";
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';

import SelectTemplateTable from './SelectTemplateTable.js';

const styles = theme => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing.unit * 2,
  },
});

class SelectTemplateStep extends Component {

  constructor(props) {
    super(props);
    this.state = {
      data: null,
      loading: false,
      error: false,
    };
  }

  renderError() {
    const msg = this.props.errorMessage ? this.props.errorMessage : 'Error';
    return <Typography>{msg}</Typography>;
  }
  renderLoading() {
    return <Typography>Loading...</Typography>;
  }
  renderLabel() {
    return <Typography>Select Template</Typography>;
  }
  renderContent() {
    const { data } = this.props.data;
    return(
      <div className={classes.root}>
        <SelectTemplateTable data={data} />
      </div>
    );
  }

  render() {
    if (this.props.loading) {
      return this.renderLoading();
    } else if (this.props.data) {
      return this.renderContent();
    } else {
      return this.renderError();
    }
  }    
}

SelectTemplateStep.propTypes = {
  classes: PropTypes.object.isRequired,
  dataProvider: PropTypes.object.isRequired,
};

export default withStyles(styles)(SelectTemplateStep);
