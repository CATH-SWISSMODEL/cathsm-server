export default class Seq {
  constructor(args) {
    const { id, seq } = args;
    this.id = id;
    this.seq = seq;
  }
  length() {
    return this.seq.length;
  }
}
