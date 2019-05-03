import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';

const styles = theme => ({
  container: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  helpTitle: {
    fontSize: 14,
  },
  querySequence: {
    marginLeft: theme.spacing.unit,
    marginRight: theme.spacing.unit,
  },
  querySequenceInput: {
    fontFamily: "Consolas, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace",
    fontSize: 12,
    lineHeight: 1.2,
  },
});
  
class QuerySequence extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
        error: false,
        errorMessage: null,
        queryFasta: "",
    };
    
    // This binding is necessary to make `this` work in the callback
    this._handleTextFieldChange = this._handleTextFieldChange.bind(this);
  }

  setError(msg) {
    this.setState({
      error: true,
      errorMessage: msg,
    });
  }

  _handleTextFieldChange(e) {
    const queryFasta = e.target.value;
    this.setSequenceFromFasta(queryFasta);
  }

  setSequenceFromFasta(queryFasta) {
    this.setState({ queryFasta });
    queryFasta = queryFasta.trim();
    if ( queryFasta === "" ) {
      this.setState({ error: false, errorMessage: null, queryId: null, querySequence: null });
      return;
    }
    const lines = queryFasta.split('\n');
    const header = lines.shift();
    if ( ! header.startsWith('>') ) {
      return this.setError("Expected FASTA header to start with '>'");
    }
    const id_re = /^>(\S+)/;
    const id_match = header.match(id_re);
    if ( !id_match ) {
      return this.setError(`Failed to parse ID from FASTA header '${header}'`);
    }
    const id = id_match[1];
    let seq = '';
    lines.forEach(function(line, line_num) {
      if( line.match(id_re) ) {
        return;
      }
      seq += line.trim();
    });
    console.log("Calling onChange with seq details", this.props, id, seq);
    this.props.onChange(id, seq);
  }

  getFasta() {
    if ( this.state.queryId && this.state.querySequence ) {
      return '>' + this.state.queryId + '\n' + this.state.querySequence + '\n';
    }
    else {
      return;
    }
  }

  renderError() {

  }
  
  render() {
    const { classes } = this.props;
    const helperText = this.state.errorMessage ? this.state.errorMessage 
      : "Protein sequence should be in FASTA format";
    const onExampleScanResults = this.props.onExampleScanResults; 

    return (
      <div className={classes.root}>
        <Grid container spacing={24}>
          <Grid item xs={8}>
            <TextField
              InputProps={{ classes: { input: classes.querySequenceInput } }}
              className={classes.querySequence}
              id="query-sequence"
              label="Query Protein Sequence"
              placeholder="Paste your query protein sequence here"
              helperText={helperText}
              multiline
              autoFocus
              value={this.state.queryFasta}
              error={this.state.error}
              required
              fullWidth
              margin="normal"
            />
          </Grid>
          <Grid item xs={4}>
            <Card className={classes.card}>
              <CardContent>
                <Typography>
                  Copy/paste a protein sequence into this form
                  then click 'Next'.
                </Typography>
              </CardContent>
              <CardActions>
                  <Button size="small" color="primary" onClick={this._handleExampleSequenceClick}>
                  Example Sequence
                  </Button>
                  <Button size="small" color="primary" onClick={onExampleScanResults}>
                  Example Results
                  </Button>
                  <Button size="small" color="primary">
                  Learn More
                  </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </div>);
  }
}

QuerySequence.propTypes = {
  classes: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onExampleScanResults: PropTypes.func,
  queryId: PropTypes.string,
  querySequence: PropTypes.string,
};

export default withStyles(styles)(QuerySequence);

