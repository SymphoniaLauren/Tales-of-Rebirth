#ifndef __SCEIO_H__
#define __SCEIO_H__

#include "types.h"

void* memset(void*, int, unsigned int);
int printf(char*, ...);

#define DATA_CACHE_FLUSH 0

#define SCE_GS_SET_TEX0_1   SCE_GS_SET_TEX0
#define SCE_GS_SET_TEX0_2   SCE_GS_SET_TEX0
#define SCE_GS_SET_TEX0(tbp, tbw, psm, tw, th, tcc, tfx, \
            cbp, cpsm, csm, csa, cld) \
    ((u_long)(tbp)         | ((u_long)(tbw) << 14) | \
    ((u_long)(psm) << 20)  | ((u_long)(tw) << 26) | \
    ((u_long)(th) << 30)   | ((u_long)(tcc) << 34) | \
    ((u_long)(tfx) << 35)  | ((u_long)(cbp) << 37) | \
    ((u_long)(cpsm) << 51) | ((u_long)(csm) << 55) | \
    ((u_long)(csa) << 56)  | ((u_long)(cld) << 61))

#define SCE_GS_SET_CLAMP_1 SCE_GS_SET_CLAMP
#define SCE_GS_SET_CLAMP_2 SCE_GS_SET_CLAMP
#define SCE_GS_SET_CLAMP(wms, wmt, minu, maxu, minv, maxv) \
    ((u_long)(wms) | ((u_long)(wmt) << 2) | ((u_long)(minu) << 4) | ((u_long)(maxu) << 14) | ((u_long)(minv) << 24) | ((u_long)(maxv) << 34))

#define SCE_GS_SET_ALPHA_1 SCE_GS_SET_ALPHA
#define SCE_GS_SET_ALPHA_2 SCE_GS_SET_ALPHA
#define SCE_GS_SET_ALPHA(a, b, c, d, fix)                    \
    ((u_long)(a) | ((u_long)(b) << 2) | ((u_long)(c) << 4) | \
     ((u_long)(d) << 6) | ((u_long)(fix) << 32))

#define SCE_GS_SET_TEST_1 SCE_GS_SET_TEST
#define SCE_GS_SET_TEST_2 SCE_GS_SET_TEST
#define SCE_GS_SET_TEST(ate, atst, aref, afail, date, datm, zte, ztst) \
    ((u_long)(ate) | ((u_long)(atst) << 1) |                           \
     ((u_long)(aref) << 4) | ((u_long)(afail) << 12) |                 \
     ((u_long)(date) << 14) | ((u_long)(datm) << 15) |                 \
     ((u_long)(zte) << 16) | ((u_long)(ztst) << 17))

#define SCE_GS_SET_TEX1_1 SCE_GS_SET_TEX1
#define SCE_GS_SET_TEX1_2 SCE_GS_SET_TEX1
#define SCE_GS_SET_TEX1(lcm, mxl, mmag, mmin, mtba, l, k) \
    ((u_long)(lcm) | ((u_long)(mxl) << 2) |               \
     ((u_long)(mmag) << 5) | ((u_long)(mmin) << 6) |      \
     ((u_long)(mtba) << 9) | ((u_long)(l) << 19) |        \
     ((u_long)(k) << 32))

typedef enum SCE_GS_REG {
    SCE_GS_PRIM=0,
    SCE_GS_RGBAQ=1,
    SCE_GS_ST=2,
    SCE_GS_UV=3,
    SCE_GS_XYZF2=4,
    SCE_GS_XYZ2=5,
    SCE_GS_TEX0_1=6,
    SCE_GS_TEX0_2=7,
    SCE_GS_CLAMP_1=8,
    SCE_GS_CLAMP_2=9,
    SCE_GS_FOG=10,
    SCE_GS_XYZF3=12,
    SCE_GS_XYZ3=13,
    SCE_GS_TEX1_1=20,
    SCE_GS__TEX1_2=21,
    SCE_GS_TEX2_1=22,
    SCE_GS_TEX2_2=23,
    SCE_GS_XYOFFSET_1=24,
    SCE_GS_XYOFFSET_2=25,
    SCE_GS_PRMODECONT=26,
    SCE_GS_PRMODE=27,
    SCE_GS_TEXCLUT=28,
    SCE_GS_SCANMSK=34,
    SCE_GS_MIPTBP1_1=52,
    SCE_GS_MIPTBP1_2=53,
    SCE_GS_MIPTBP2_1=54,
    SCE_GS_MIPTBP2_2=55,
    SCE_GS_TEXA=59,
    SCE_GS_FOGCOL=61,
    SCE_GS_TEXFLUSH=63,
    SCE_GS_SCISSOR_1=64,
    SCE_GS_SCISSOR_2=65,
    SCE_GS_ALPHA_1=66,
    SCE_GS_ALPHA_2=67,
    SCE_GS_DIMX=68,
    SCE_GS_DTHE=69,
    SCE_GS_COLCLAMP=70,
    SCE_GS_TEST_1=71,
    SCE_GS_TEST_2=72,
    SCE_GS_PABE=73,
    SCE_GS_FBA_1=74,
    SCE_GS_FBA_2=75,
    SCE_GS_FRAME_1=76,
    SCE_GS_FRAME_2=77,
    SCE_GS_ZBUF_1=78,
    SCE_GS_ZBUF_2=79,
    SCE_GS_BITBLTBUF=80,
    SCE_GS_TRXPOS=81,
    SCE_GS_TRXREG=82,
    SCE_GS_TRXDIR=83,
    SCE_GS_HWREG=84,
    SCE_GS_SIGNAL=96,
    SCE_GS_FINISH=97,
    SCE_GS_LABEL=98,
    SCE_GS_NOP=127
} SCE_GS_REG;

/* Seek Code */
#ifndef SCE_SEEK_SET
#define SCE_SEEK_SET        (0)
#endif
#ifndef SCE_SEEK_CUR
#define SCE_SEEK_CUR        (1)
#endif
#ifndef SCE_SEEK_END
#define SCE_SEEK_END        (2)
#endif

/* Flag for sceOpen() */
#define SCE_RDONLY      0x0001
#define SCE_WRONLY      0x0002
#define SCE_RDWR        0x0003
#define SCE_NBLOCK      0x0010  /* Non-Blocking I/O */
#define SCE_APPEND      0x0100  /* append (writes guaranteed at the end) */
#define SCE_CREAT       0x0200  /* open with file create */
#define SCE_TRUNC       0x0400  /* open with truncation */
#define SCE_EXCL        0x0800  /* exclusive create */
#define SCE_NOBUF       0x4000  /* no device buffer and console interrupt */
#define SCE_NOWAIT      0x8000  /* asyncronous i/o */

extern int  sceOpen(const char *filename, int flag, ...);
extern int  sceClose(int fd);
extern int  sceRead(int fd, void *buf, int nbyte);
extern int  sceWrite(int fd, const void *buf, int nbyte);
extern int  sceLseek(int fd, int offset, int where);

#endif /* __SCEIO_H__ */