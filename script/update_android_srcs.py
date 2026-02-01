#!/usr/bin/env python3
#
#  Copyright (c) 2026, The OpenThread Authors.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#

#
# This script automatically updates the 'srcs' list in the Android.bp file.
# It scans the 'src' directory for all .cpp files, excludes specified files
# and directories, and then replaces the 'srcs' list within the
# 'ot-daemon-defaults' cc_defaults block in Android.bp.
#
# Usage:
# Run this script from the root directory of the ot-br-posix project:
#   python3 script/update_android_srcs.py
#

import os
import re

def update_android_bp_srcs(bp_file="Android.bp", src_dir="src"):
    # Read the content of Android.bp
    with open(bp_file, "r") as f:
        bp_content = f.read()

    # Find all .cpp files under the src_dir
    cpp_files = []
    for root, dirs, files in os.walk(src_dir):
        # Exclude specific directories
        dirs[:] = [d for d in dirs if d not in ["web", "rest", "openwrt", "proto", "dbus", "telemetry"]]
        for file in files:
            if file.endswith(".cpp"):
                cpp_files.append(os.path.join(root, file))
    cpp_files.sort()

    # Exclude specific files
    exclude_files = [
        "src/agent/main.cpp",
        "src/android/otdaemon_fuzzer.cpp",
        "src/backbone_router/dua_routing_manager.cpp",
        "src/backbone_router/nd_proxy.cpp",
        "src/common/api_strings.cpp",
        "src/host/posix/netif_unix.cpp",
        "src/mdns/mdns_avahi.cpp",
        "src/mdns/mdns_mdnssd.cpp",
        "src/mdns/mdns_openthread.cpp",
        "src/utils/sha256.cpp",
        "src/utils/telemetry_retriever_border_agent.cpp",
    ]
    cpp_files = [f for f in cpp_files if f not in exclude_files]

    # Format the file paths for the srcs list items
    srcs_items = []
    for cpp_file in cpp_files:
        srcs_items.append(f'        "{cpp_file}",')
    srcs_items_str = "\n".join(srcs_items)

    # Replace the old srcs list content with the new one
    # This regex looks for the content within the srcs list in ot-daemon-defaults
    pattern = re.compile(
        r"(cc_defaults\s*{\s*name:\s*\"ot-daemon-defaults\",[\s\S]*?srcs:\s*\[\n)[\s\S]*?(\s*\][\s\S]*?shared_libs:)",
        re.MULTILINE
    )

    replacement = r"\1" + srcs_items_str + r"\2"
    new_bp_content = pattern.sub(replacement, bp_content)

    if new_bp_content != bp_content:
        # Write the updated content back to Android.bp
        with open(bp_file, "w") as f:
            f.write(new_bp_content)
        print(f"Successfully updated {bp_file} with {len(cpp_files)} source files.")
    else:
        print(f"No changes needed for {bp_file}.")

if __name__ == "__main__":
    update_android_bp_srcs()