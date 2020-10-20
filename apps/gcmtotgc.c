// gcmtotgc.c -- Zochwar & Plootid 2005
// Version 0.1
#include <stdio.h>
//#include <winsock.h>

int main(int argc, char **argv) {

  FILE *tgcout, *gcmin;
  unsigned long tgcheader[14];
  unsigned long temp[6];
  unsigned long fileareastart, fileareaend;
  char c;
  int i;
  
  if (argc < 2) {
    printf("Usage: %s <infile.gcm> <outfile.tgc>\n", argv[0]);
    return 1;
  }

  if (!(gcmin = fopen(argv[1], "rb"))) {
    printf("Error: Couldn't open file %s\n", argv[1]);
    return 1;
  }

  tgcheader[0] = 0xAE0F38A2;	// tgc id?
  tgcheader[1] = 0x00000000;	// Unknown
  tgcheader[2] = 0x00008000;	// tgc header size?
  tgcheader[3] = 0x00100000;	// Unknown (any ideas?)
  fseek(gcmin, 0x420L, SEEK_SET);
  fread(temp, 4, 6, gcmin);
  tgcheader[4] = ntohl(temp[1]) + tgcheader[2]; // FST Offset (from .tgc)
  tgcheader[5] = ntohl(temp[2]);		// FST Size
  tgcheader[6] = ntohl(temp[3]);		// FST Maz Size (?)
  tgcheader[7] = ntohl(temp[0]) + tgcheader[2];	// DOL Offset (from .tgc)
  tgcheader[8] = 0;	// We'll calculate the DOL Size later
  tgcheader[9] = ntohl(temp[5]) + tgcheader[2];	// File Area Start (from .tgc)
//10: We'll calculate the File Area Size later
  tgcheader[11]= 0;				// Banner location? (ignored)
  tgcheader[12]= 0;				// Banner Size? (ignored)
//13: We'll calculate the FST Spoof amount later

  // Calculate DOL size

  fseek(gcmin, tgcheader[7] - tgcheader[2], SEEK_SET);
  for (i = 0; i < 18; i++) {
    fread(temp, 4, 1, gcmin);
    if (ntohl(temp[0]) > tgcheader[8]) {
      temp[1] = i;
      tgcheader[8] = ntohl(temp[0]);
    }
  }
  fseek(gcmin, 72 + (temp[1] * 4), SEEK_CUR);
  fread(temp, 4, 1, gcmin);
//  tgcheader[8] = (tgcheader[8] + ntohl(temp[0]) + 255) & 0xFFFFFF00;

  // Parse FST
  fseek(gcmin, tgcheader[4] - tgcheader[2], SEEK_SET);	// Seek to FST
  fileareastart = 0x57058000L;
  fileareaend = 0;
  fread(temp, 4, 3, gcmin);
  for (i = ntohl(temp[2]) - 1; i > 0; i--) {
    fread(temp, 4, 3, gcmin);
    if (!(ntohl(temp[0]) & 0x01000000)) {       // If not a directory
      if (fileareastart > ntohl(temp[1])) fileareastart = ntohl(temp[1]);
      if (fileareaend <= ntohl(temp[1]))
	fileareaend = ntohl(temp[1]) + ntohl(temp[2]);
    }
  }

  tgcheader[10]= (fileareaend - fileareastart + 32767) & 0xFFFF8000;
  tgcheader[13]= fileareastart;			// FST Spoof Amount

  for (i = 0; i < 14; i++) tgcheader[i] = htonl(tgcheader[i]); //Byte-swap
  
  if (!(tgcout = fopen(argv[2], "w+b"))) {
    printf("Error: Couldn't open file %s\n", argv[2]);
    fclose(gcmin);
    return 1;
  }

  printf("GCMtoTGC V0.1 by Zochwar & Plootid 2005\n\n");

  fwrite(tgcheader, 4, 14, tgcout);
  fflush(tgcout);
  fseek(tgcout, ntohl(tgcheader[2]), SEEK_SET);
  fseek(gcmin, 0, SEEK_SET);
  
  printf("Writing Header...\n");
  for(i = ntohl(tgcheader[9]) - ntohl(tgcheader[2]); i > 0; i--) {
    c = getc(gcmin);
    putc(c, tgcout);
  }
  fflush(tgcout);
  
  fseek(gcmin, fileareastart, SEEK_SET);
  printf("Writing Files...\n");
  for (i = fileareaend - fileareastart; i > 0; i--) {
    c = getc(gcmin);
    putc(c, tgcout);			// Buffering? What's that?
  }
  fflush(tgcout);
  close(gcmin);

  if (i = ((ftell(tgcout) + 0x7FFF) & 0xFFFF0000) - ftell(tgcout)) {
    fseek(tgcout, i-1, SEEK_CUR);
    fputc('\0', tgcout);
  }
  
  fflush(tgcout);

  fclose(tgcout);
  printf("All Done!\n");
  return 0;
}
