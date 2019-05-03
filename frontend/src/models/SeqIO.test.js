const fs = require('fs');
const path = require('path');

import Seq from "./Seq";
import SeqMeta from "./SeqMeta";
import SeqIO from "./SeqIO";

const testFastaId = 'tr|A0A0Q0Y989|A0A0Q0Y989_9BACI';
const testFastaPath = path.join(__dirname, '..', 'data', 'A0A0Q0Y989.fa');
const testFasta = fs.readFileSync(testFastaPath, 'utf8');

const testFastaSeq = testFasta.split(/\n/).slice(1).join('');

describe("SeqMeta", () => {
  it("newFromFastaHdr", () => {
    const meta = SeqMeta.newFromFastaHeader('>' + testFastaId);
    expect(meta.id).toBe('tr|A0A0Q0Y989|A0A0Q0Y989_9BACI');
  });
});

describe("Seq", () => {
  it("create new okay", () => {
    const id = 'query_id', seqstr = 'MNDFHRDTWAEVDLDAIYDNVANLRRLLPDDTHIMAVVKANAYGHGD';
    const seq = new Seq({ id, seq: seqstr });
    expect(seq.id).toBe(id);
    expect(seq.seq).toBe(seqstr);
  });
})

describe("SeqIO", () => {

  // it("create new needs args", () => {
  //   const io = new SeqIO();
  //   expect(io).toBeDefined();
  // });

  it("create new looks okay", () => {
    const io = new SeqIO({ format: 'fasta', source: testFasta });
    const seq = io.next();
    expect(seq.id).toBe(testFastaId);
    expect(seq.seq).toBe(testFastaSeq);
  });

});
