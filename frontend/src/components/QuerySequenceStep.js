import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import FormControl from '@material-ui/core/FormControl';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';
import CardActions from '@material-ui/core/CardActions';

const styles = theme => ({
  root: {
    width: '100%',
    backgroundColor: theme.palette.background.paper,
  },
  section: {
    margin: theme.spacing(3, 2),
  },
  helpTitle: {
    fontSize: 14,
  },
  formControl: {

  },
  querySequence: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
  },
  querySequenceInput: {
    fontFamily: "Consolas, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace",
    fontSize: 12,
    lineHeight: 1.2,
  },
});

const exampleSequences = {
  'A0A0Q0Y989': 'MNDFHRDTWAEVDLDAIYDNVANLRRLLPDDTHIMAVVKANAYGHGDVQVARTALEAGASRLAVAFLDEALALREKGIEAPILVLGASRPADAALAAQQRIALTVFRSDWLEEASALYSGPFPIHFHLKMDTGMGRLGVKDEEETKRIVALIERHPHFVLEGVYTHFATADEVNTDYFSYQYTRFLHMLEWLPSRPPLVHCANSAASLRFPDRTFNMVRFGIAMYGLAPSPGIKPLLPYPLKEAFSLHSRLVHVKKLQPGEKVSYGATYTAQTEEWIGTIPIGYADGWLRRLQHFHVLVDGQKAPIVGRICMDQCMIRLPGPLPVGTKVTLIGRQGDEVISIDDVARHLETINYEVPCTISYRVPRIFFRHKRIMEVRNAIGRGESSA',
  'O014992': 'MSVVGIDLGFQSCYVAVARAGGIETIANEYSDRCTPACISFGPKNRSIGAAAKSQVISNAKNTVQGFKRFHGRAFSDPFVEAEKSNLAYDIVQLPTGLTGIKVTYMEEERNFTTEQVTAMLLSKLKETAESVLKKPVVDCVVSVPCFYTDAERRSVMDATQIAGLNCLRLMNETTAVALAYGIYKQDLPALEEKPRNVVFVDMGHSAYQVSVCAFNRGKLKVLATAFDTTLGGRKFDEVLVNHFCEEFGKKYKLDIKSKIRALLRLSQECEKLKKLMSANASDLPLSIECFMNDVDVSGTMNRGKFLEMCNDLLARVEPPLRSVLEQTKLKKEDIYAVEIVGGATRIPAVKEKISKFFGKELSTTLNADEAVTRGCALQCAILSPAFKVREFSITDVVPYPISLRWNSPAEEGSSDCEVFSKNHAAPFSKVLTFYRKEPFTLEAYYSSPSGFALSRSQFSVQKVLLSLMAPVQK',
};

class QuerySequenceStep extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      error: false,
      errorMessage: null,
      querySequenceId: "",
      querySequence: "",
    };

    // This binding is necessary to make `this` work in the callback
    this._handleTextFieldChange = this._handleTextFieldChange.bind(this);
    this._handleSubmit = this._handleSubmit.bind(this);
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

  _handleSubmit(ev) {
    const { querySequence, querySequenceId } = this.state;
    this.props.onSubmit(ev, { id: querySequenceId, seq: querySequence });
  }

  setSequenceFromFasta(queryFasta) {
    this.setState({ queryFasta });
    queryFasta = queryFasta.trim();
    if (queryFasta === "") {
      this.setState({ error: false, errorMessage: null, queryId: null, querySequence: null });
      return;
    }
    const lines = queryFasta.split('\n');
    const header = lines.shift();
    if (!header.startsWith('>')) {
      return this.setError("Expected FASTA header to start with '>'");
    }
    const id_re = /^>(\S+)/;
    const id_match = header.match(id_re);
    if (!id_match) {
      return this.setError(`Failed to parse ID from FASTA header '${header}'`);
    }
    const id = id_match[1];
    let seq = '';
    lines.forEach(function (line, line_num) {
      if (line.match(id_re)) {
        return;
      }
      seq += line.trim();
    });
    console.log("Calling onChange with seq details", this.props, id, seq);
    this.props.onChange(id, seq);
  }

  _handleExampleClick(exampleId) {
    const exampleSeq = exampleSequences[exampleId];
    console.log("_handleExampleClick", this, exampleId, exampleSeq);
    this.setState(state => {
      return { querySequenceId: exampleId, querySequence: exampleSeq };
    });
  }

  getFasta() {
    if (this.state.queryId && this.state.querySequence) {
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

    return (
      <div className={classes.root}>
        <div className={classes.section}>
          <FormControl fullWidth>
            <TextField
              InputProps={{ classes: { input: classes.querySequenceInput } }}
              className={classes.querySequence}
              id="query-sequence"
              label="Query Protein Sequence"
              placeholder="Paste your protein sequence here"
              helperText="Protein sequence should be a string of amino-acids"
              multiline
              autoFocus
              value={this.state.querySequence}
              error={this.state.error}
              required
            />
          </FormControl>
          <FormControl>
            <TextField
              InputProps={{ classes: { input: classes.querySequenceInput } }}
              className={classes.querySequence}
              id="query-sequence-id"
              label="Sequence ID"
              placeholder="Add a name/id for your sequence"
              helperText="Add a name/id for your sequence"
              value={this.state.querySequenceId}
              error={this.state.error}
              required
            />
          </FormControl>
        </div>
        <Divider variant="middle" />
        <div className={classes.section}>
          <CardActions>
            <Button variant="contained"
              onClick={() => this._handleExampleClick("A0A0Q0Y989")}>Example1</Button>
            <Button variant="contained"
              onClick={() => this._handleExampleClick("O014992")}>Example2</Button>
            <Button variant="contained" color="secondary"
              onClick={this._handleClear}>Clear</Button>
            <Button variant="contained" color="primary"
              onClick={this._handleSubmit}>Submit</Button>
          </CardActions>
        </div>
      </div >);
  }
}

QuerySequenceStep.propTypes = {
  classes: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  queryId: PropTypes.string,
  querySequence: PropTypes.string,
};

export default withStyles(styles)(QuerySequenceStep);

