#include "types.h"
#include "rebirth.h"
#include "sceio.h"
#include "init.h"

#define CUSTOM_FILE_SIZE 0x40
#define OLD_HEAP_BASE (void*)0x00391400
#define NEW_HEAP_BASE 0x003A0000
#define MAX_MONSTER_SIZE 0x1C00
#define CUSTOM_CODE_FID 10227
#define CUSTOM_CODE_BASE (void*)0x00393000
#define MNU_MONSTER_FID 10264

void load_custom_files() {
    file_desc file;
    int code_size, monster_size, used_size;

    // // Load custom code file
    memset(&file, 0, sizeof(file));
    file.file_id = CUSTOM_CODE_FID;
    file.file_size = code_size = get_file_size(file.file_id, 0);
    file.addr = CUSTOM_CODE_BASE;
    file.flags = LOAD_BLOCKING;
    file.unk12 = 0;
    file_pls(&file);
    
    printf("###########################\n");
    printf("%s\n", file.addr);
    printf("###########################\n");
    // load_from_host0();
    
    // Load custom mnu_monster file
    memset(&file, 0, sizeof(file));
    file.file_id = MNU_MONSTER_FID;
    file.file_size = monster_size = get_file_size(file.file_id, 0);
    file.addr = OLD_HEAP_BASE;
    file.flags = LOAD_BLOCKING;
    file.unk12 = 0;
    file_pls(&file);

    // The files above are loaded outside the heap area
    // so check we aren't overflowing
    used_size = (u32)OLD_HEAP_BASE + monster_size + code_size;
    if (monster_size > MAX_MONSTER_SIZE || used_size > NEW_HEAP_BASE) {
        printf("Data beyond max size!!!");
        // Avoid bad behavior and just loop forever
        while(1);
    }
}

// void load_from_host0() {
//     int fd;
//     int filesize;
//     void* addr;

//     // open a file to read and check its size
//     fd = sceOpen("host0:10227.bin", SCE_RDONLY);
//     if (fd < 0) {
//         printf("Couldn't open host0 file\n");
//     } else {
//         filesize = sceLseek(fd, 0, SCE_SEEK_END);
//         sceLseek(fd, 0, SCE_SEEK_SET);
//         addr = alloc_EE(filesize, 0, 0);

//         sceRead(fd, addr, filesize);
//         sceClose(fd);
//     }
// }

extern void update_tex0();

void init_all_the_things(void) {
    ThreadParam thread;
    int i;
    int local_328;
    u32 cd_mode;
    u8 *local_31c;
    file_desc file;
    unk_struct mnuenv_maybe;

    // Init file system IOP module needs the stack
    // aligned to 0x10, so ensure that's the case
    STACK_ALIGN();
    
    func_001002A8();
    cd_mode = 2;
    init_heap();
    sceSifInitRpc(0);
    sceCdInit(0);
    sceCdMode(cd_mode);
    sceCdInit(5);
    sceSifExitCmd();
    while (!sceSifRebootIop("cdrom0:\\IOPRP300.IMG;1"));
    while (!sceSifSyncIop());
    sceSifInitRpc(0);
    sceSifLoadFileReset();
    sceFsReset();
    sceCdInit(0);
    sceCdMode(cd_mode);
    sceSifInitIopHeap();
    sceDevVif0Reset();
    sceDevVu0Reset();
    sceVpu0Reset();
    sceDmaReset(1);
    sceGsResetPath();
    ChangeThreadPriority(GetThreadId(), 0x60);
    thread.entry = &rotate_thread_func;
    thread.stack = &rotate_thread_stack;
    thread.stackSize = 0x400;
    thread.gpReg = &_gp;
    thread.initPriority = 0x7f;
    rotate_thread_id = CreateThread(&thread);
    StartThread(rotate_thread_id, 0);
    func_0010E1E8();
    func_0010F830();
    init_filesystem(); // init IOP filesystem module

    gMain.unk666 = 1;
    gMain.unk667 = 1;

    func_0010F148();
    func_0010ED38();
    // func_0010BD10(); // It's empty
    sceGsResetGraph(0, 1, 2, 1);
    func_00102608();
    sceGsPutDispEnv(&gMain);
    local_328 = func_0010EEF8();
    gMain.unk666 ^= 1;
    func_0010ED38();
    while (local_328 != func_0010EEF8()) {
        func_0010ED38();
    }
    func_0012B268();
    func_0012ACA8(1, 0, 0);
    func_001045F0();
    func_00108710();
    // func_0010D408(); // It's empty
    func_001002E8();
    custom_memcpy(&custom_temp, &custom, 0x88);
    func_001407F0(0x800);
    func_00119010();
    func_0010D288();
    func_00117120();
    func_00118C50();
    func_0010ED38();
    func_00104620(); // Load images
    func_00113BC0();
    func_00108668();

    // Load custom files
    load_custom_files();

    memset(&file, 0, sizeof(file));
    while ((local_31c = sceSifAllocSysMemory(1, 0x1c000, 0)) == 0);
    file.addr = local_31c;
    file.start_offset = file.file_size = 0;
    file.flags = LOAD_BLOCKING | IS_COMPRESSED | IS_IOP_MODULE;
    file.unk12 = 0;
    for (i = 0; i < 5; i++) {
        file.file_id = i + 3;
        file_pls(&file);
    }
    init_controller();
    init_memorycard();
    func_0012D940(0);
    generate_sin();
    func_0011A2C0();
    init_party_data(0);
    func_00171C18();
    while (!func_001312D8()) {
        func_0010F3E0();
    }
    while (func_00131990() == 1) {
        func_0010F3E0();
    }
    if ((func_00131950() & 8) == 0) {
        memset(&mnuenv_maybe, 0, sizeof(unk_struct));
        mnuenv_maybe.unk4 = alloc_EE(0x80000, 0, 0);
        mnuenv_maybe.unk8 = 0x80000;
        mnuenv_maybe.unkC = 4;
        mnuenv_maybe.unk18 = 0x8000;
        mnuenv_maybe.unk1A = 0x8000;
        func_00176C80(&mnuenv_maybe);
        func_00171F18(0xf, 0);
        free_EE(mnuenv_maybe.unk4);
    }
    func_00103100();
    file.addr = local_31c;
    file.start_offset = file.file_size = 0;
    file.flags = LOAD_BLOCKING | IS_COMPRESSED | IS_IOP_MODULE;
    file.unk12 = 0;
    for (i = 5; i < 10; i++) {
        file.file_id = i + 3;
        file_pls(&file);
    }
    sceSifFreeSysMemory(local_31c);
    func_0017A5A0();
    func_00101E18();
    sceMpegInit();
    func_001492B8();
    func_00121460();
    func_0017A660();
    func_001005A8();
    // dbg_print("initialize debug window\n");
    // func_0010D440();
    // dbg_print("initialize field res data\n");
    func_001533C0();
    // dbg_print("initialize actinfo\n");
    func_0012BF58();
    // dbg_print("initialize res chr\n");
    func_00100760();
    func_0013FFB0();
    func_00103650();
    func_0010ED38();
    func_00102608();
    func_0012D9D0();
    func_0010EA78();
}
