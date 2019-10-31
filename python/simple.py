from bcc import BPF
import ctypes as ct
from struct import pack

# define BPF program
prog = """
#include <uapi/linux/ptrace.h>
#include <linux/fs.h>
#include <linux/sched.h>

BPF_PERF_OUTPUT(general_events);

struct data_t {
    u64 pid;
    u64 tid;
    //u64 len;
    char name[TASK_COMM_LEN];
    char filename[128];
};

int track(struct pt_regs  *ctx, int dfd, const char __user *fn) {
    if (fn == NULL)
        return 0;
    struct data_t data = {};
    u64 pid = bpf_get_current_pid_tgid();
    u32 tpid = pid;
    u32 gpid = (pid>>32);
    //if (upid != 3187) return 0;
    data.pid = gpid;
    data.tid = tpid;
    //data.len = count;
    //const unsigned char* fn = file->f_path.dentry->d_iname;
    // copy the name
    bpf_get_current_comm(&data.name, sizeof(data.name));
    if ((data.name[0] != 'd') || (data.name[1] != 'o') || (data.name[2] != 'c')|| (data.name[3] != 'k')) return 0;
    bpf_probe_read(&data.filename, sizeof(data.filename), fn);
    data.filename[sizeof(data.filename)-1] = 0;
    general_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

# load BPF program
b = BPF(text=prog)
b.attach_kprobe(event="do_sys_open", fn_name="track")

TASK_COMM_LEN = 16
class MyData(ct.Structure):
    _fields_ = [
        ("pid", ct.c_ulonglong),
        ("tid", ct.c_ulonglong),
        # ("length", ct.c_ulonglong),
        ("name", ct.c_char * TASK_COMM_LEN),
        ("file_name", ct.c_char * 128),
    ]

# header
print("%-8s %-8s %-16s %-32s" % ("PID", "TASK-ID", "CMD", "FILENAME",))


# process event
def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(MyData)).contents
    print(
        "%-8s %-8s %-16s %-32s" % (
            event.pid,
            event.tid,
            event.name,
            event.file_name,
        )
    )

# loop with callback to print_event
b["general_events"].open_perf_buffer(print_event)
# format output
while True:
    b.kprobe_poll()



