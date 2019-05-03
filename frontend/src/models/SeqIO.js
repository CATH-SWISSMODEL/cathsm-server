import Seq from './Seq';
import SeqMeta from './SeqMeta';

export default class SeqIO {

  constructor( args ) {
    const { format, source } = args;
    this.format = format ? format.toLowerCase() : undefined;
    this.source = source;
    this.currentPos = 0;
  }

  nextLine() {
    const sourceLength = this.source.length;
    if ( this.currentPos >= sourceLength ) {
      return;
    }

    let line = '';
    for( let pos=this.currentPos; pos < sourceLength; pos++ ) {
      const char = this.source[pos];
      line += char;
      if ( char === '\n' ) {
        break;
      }
    }
    this.currentPos += line.length;
    return line;
  }

  next() {
    if ( this.format === 'fasta' ) {
      return this.nextFasta();
    }
  }

  nextFasta() {
    // read un
    let currentId = '';
    let currentSeq = '';

    const hdr = this.nextLine();
    const seqMeta = SeqMeta.newFromFastaHeader( hdr );
    const id = seqMeta.id;

    let seq = '';    
    while (1) {
      let line = this.nextLine();
      if ( ! line || typeof(line) === 'undefined' ) {
        break;
      }
      if ( line.startsWith('>') ) {
        this.currentPos -= line.length;
        break;
      }
      line = line.trim();
      seq += line;
    }
    return new Seq({ id, seq });
  }
}
