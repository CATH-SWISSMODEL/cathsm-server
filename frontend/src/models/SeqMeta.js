export default class SeqMeta {

  constructor(args) {
    const { id } = args;
    this.id = id;
  }

  static newFromFastaHeader(hdr) {
    const parts = hdr.match(/^>(\S+)/);
  
    if( ! parts ) {
      throw Error(`failed to parse fasta header (${hdr}): expected string to start with '>'`);
    }
  
    const id = parts[1];
  
    return new SeqMeta({ id });
  }
}
