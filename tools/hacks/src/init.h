#ifndef __INIT_H__
#define __INIT_H__

#include "types.h"

extern void* custom;
extern void* custom_temp;
extern void* _gp;
extern void (*rotate_thread_func)(void*);
extern int rotate_thread_id;
extern int rotate_thread_stack[];

typedef struct ThreadParam {
    s32     status;
    void    (*entry)(void *);
    void    *stack;
    s32     stackSize;
    void    *gpReg;
    s32     initPriority;
    s32     currentPriority;
    u32     attr;
    u32     option;
    s32     waitType;
    s32     waitId;
    s32     wakeupCount;
} ThreadParam;

typedef struct unk_struct {
    s32 unk0;
    void* unk4;
    s32 unk8;
    s32 unkC;
    s32 unk10;
    s32 unk14;
    u16 unk18;
    u16 unk1A;
} unk_struct;

extern void init_heap();
extern void sceSifInitRpc(int);
extern void sceCdInit(int);
extern void sceCdMode(int);
extern void sceCdInit(int);
extern void sceSifExitCmd();
extern int sceSifRebootIop(char*);
extern int sceSifSyncIop();
extern void sceSifInitRpc(int);
extern void sceSifLoadFileReset();
extern void sceFsReset();
extern void sceCdInit(int);
extern void sceCdMode(int);
extern void sceSifInitIopHeap();
extern void sceDevVif0Reset();
extern void sceDevVu0Reset();
extern void sceVpu0Reset();
extern void sceDmaReset(int);
extern void sceGsResetPath();
extern int GetThreadId();
extern void ChangeThreadPriority(int, int);
extern int CreateThread(ThreadParam*);
extern void StartThread(int, int);
extern void func_0010E1E8();
extern void func_0010F830();
extern void init_filesystem();
extern u32 get_file_size(int, int);
extern void file_pls(file_desc*);
extern void func_0010F148();
extern void func_0010ED38();
extern void sceGsResetGraph(int, int, int, int);
extern void func_00102608();
extern void sceGsPutDispEnv(void*);
extern int func_0010EEF8();
extern void func_0010ED38();
extern void func_0012B268();
extern void func_0012ACA8(int, int, int);
extern void func_001045F0();
extern void func_00108710();
extern void func_001002E8();
extern void custom_memcpy(void*, void*, u32);
extern void func_001407F0(u32);
extern void func_00119010();
extern void func_0010D288();
extern void func_00117120();
extern void func_00118C50();
extern void func_0010ED38();
extern void func_00104620();
extern void func_00113BC0();
extern void func_00108668();
extern void* sceSifAllocSysMemory(int, int, int);
extern void init_controller();
extern void init_memorycard();
extern void func_0012D940(int);
extern void generate_sin();
extern void func_0011A2C0();
extern void init_party_data(int);
extern void func_00171C18();
extern int func_001312D8();
extern int func_00131990();
extern void func_0010F3E0();
extern void update_tex0();
extern int func_00131950();
extern void* alloc_EE(u32, u32, u32);
extern void func_00176C80(unk_struct*);
extern void func_00171F18(int, int);
extern void free_EE(void*);
extern void func_00103100();
extern void sceSifFreeSysMemory(u8*);
extern void func_0017A5A0();
extern void func_00101E18();
extern void sceMpegInit();
extern void func_001492B8();
extern void func_00121460();
extern void func_0017A660();
extern void func_001005A8();
extern void func_001533C0();
extern void func_0012BF58();
extern void func_00100760();
extern void func_0013FFB0();
extern void func_00103650();
extern void func_0010ED38();
extern void func_00102608();
extern void func_0012D9D0();
extern void func_0010EA78();
extern void func_001002A8();

#endif /* __INIT_H__ */