#!/usr/bin/python
# IBM_PROLOG_BEGIN_TAG
# This is an automatically generated prolog.
#
# $Source: op-test-framework/testcases/OpTestRTCdriver.py $
#
# OpenPOWER Automated Test Project
#
# Contributors Listed Below - COPYRIGHT 2015
# [+] International Business Machines Corp.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# IBM_PROLOG_END_TAG

#  @package OpTestRTCdriver
#  RTC package for OpenPower testing.
#
#  This class will test the functionality of following drivers
#  1. RTC driver: Real time clock

import time
import subprocess
import re

import unittest

import OpTestConfiguration
from common.OpTestUtil import OpTestUtil
from common.OpTestSystem import OpSystemState

class OpTestRTCdriver(unittest.TestCase):
    def setUp(self):
        conf = OpTestConfiguration.conf
        self.cv_HOST = conf.host()
        self.cv_IPMI = conf.ipmi()
        self.cv_SYSTEM = conf.system()
        self.util = OpTestUtil()

    ##
    # @brief This function will cover following test steps
    #        1. Getting host information(OS and Kernel info)
    #        2. Loading rtc_opal module based on config option
    #        3. Testing the rtc driver functions
    #                Display the current time,
    #                set the Hardware Clock to a specified time,
    #                set the Hardware Clock from the System Time, or
    #                set the System Time from the Hardware Clock
    #                keep the Hardware clock in UTC or local time format
    #                Hardware clock compare, predict and adjust functions
    #                Hardware clock debug and test modes
    #                Reading the Hardware clock from special file instead of default
    #        4. After executing above each function reading the Hardware clock in b/w functions.
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def runTest(self):
        # TODO: run in skiroot too
        self.cv_SYSTEM.goto_state(OpSystemState.OS)

        # Get hwclock version
        l_hwclock = self.cv_HOST.host_run_command("hwclock -V;echo $?")
        # Get Kernel Version
        l_kernel = self.cv_HOST.host_get_kernel_version()

        # loading rtc_opal module based on config option
        l_config = "CONFIG_RTC_DRV_OPAL"
        l_module = "rtc_opal"
        self.cv_HOST.host_load_module_based_on_config(l_kernel, l_config, l_module)

        # Get the device files for rtc driver
        l_res = self.cv_HOST.host_run_command("ls /dev/ | grep -i --color=never rtc")
        l_files = l_res.splitlines()
        l_list = []
        for name in l_files:
            if name.__contains__("rtc"):
                l_file = "/dev/" + name
                l_list.append(l_file)
            else:
                continue
        print l_list

        # Display the time of hwclock from device files
        for l_file in l_list:
            self.read_hwclock_from_file(l_file)

        self.cv_HOST.host_read_hwclock()
        self.cv_HOST.host_set_hwclock_time("2015-01-01 10:10:10")
        self.cv_HOST.host_read_hwclock()
        self.cv_HOST.host_set_hwclock_time("2016-01-01 20:20:20")
        self.cv_HOST.host_read_hwclock()
        self.set_hwclock_in_utc("2017-01-01 10:10:10")
        self.cv_HOST.host_read_hwclock()
        self.set_hwclock_in_localtime("2014-01-01 05:05:05")
        self.cv_HOST.host_read_hwclock()
        self.cv_HOST.host_read_systime()
        self.systime_to_hwclock()
        self.cv_HOST.host_read_hwclock()
        self.systime_to_hwclock_in_utc()
        self.cv_HOST.host_read_hwclock()
        self.systime_to_hwclock_in_localtime()
        self.cv_HOST.host_read_hwclock()
        self.hwclock_to_systime()
        self.cv_HOST.host_read_hwclock()
        self.cv_HOST.host_read_systime()
        self.hwclock_in_utc()
        self.cv_HOST.host_read_hwclock()
        self.hwclock_in_localtime()
        self.cv_HOST.host_read_hwclock()
        self.hwclock_predict("2015-01-01 10:10:10")
        self.cv_HOST.host_read_hwclock()
        self.hwclock_debug_mode()
        self.cv_HOST.host_read_hwclock()
        self.hwclock_test_mode("2018-01-01 10:10:10")
        self.cv_HOST.host_read_hwclock()
        self.hwclock_adjust()
        self.cv_HOST.host_read_hwclock()
        self.hwclock_compare()
        self.cv_HOST.host_read_hwclock()

    ##
    # @brief This function reads hwclock from special /dev/... file instead of default
    #
    # @param i_file @type string: special /dev/ file
    def read_hwclock_from_file(self, i_file):
        print "Reading the hwclock from special file /dev/ ...: %s" % i_file
        l_res = self.cv_HOST.host_run_command("hwclock -r -f %s;echo $?" % i_file)
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Reading the hwclock from file failed.")

    ##
    # @brief This function sets hwclock in UTC format
    #
    # @param i_time @type string: time to set hwclock
    #                             Ex: "2016-01-01 12:12:12"
    def set_hwclock_in_utc(self, i_time):
        print "Setting the hwclock in UTC: %s" % i_time
        l_res = self.cv_HOST.host_run_command("hwclock --set --date \'%s\' --utc;echo $?" % i_time)
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock in UTC failed");

    ##
    # @brief This function sets hwclock in local time format
    #
    # @param i_time @type string: Time to set hwclock
    def set_hwclock_in_localtime(self, i_time):
        print "Setting the hwclock in localtime: %s" % i_time
        l_res = self.cv_HOST.host_run_command("hwclock --set --date \'%s\' --localtime;echo $?" % i_time)
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock in localtime failed")

    ##
    # @brief This function sets the time of hwclock from system time
    def systime_to_hwclock(self):
        print "Setting the hwclock from system time"
        l_res = self.cv_HOST.host_run_command("hwclock --systohc;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock from system time failed")

    ##
    # @brief This function sets the time of hwclock from system time in UTC format
    def systime_to_hwclock_in_utc(self):
        print "Setting the hwclock from system time, in UTC format"
        l_res = self.cv_HOST.host_run_command("hwclock --systohc --utc;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock from system time in UTC format failed")

    ##
    # @brief This function sets the time of hwclock from system time in local time format
    def systime_to_hwclock_in_localtime(self):
        print "Setting the hwclock from system time, in localtime format"
        l_res = self.cv_HOST.host_run_command("hwclock --systohc --localtime;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock from system time in localtime format failed")

    ##
    # @brief This function sets the system time from hwclock.
    def hwclock_to_systime(self):
        print "Setting the system time from hwclock"
        l_res = self.cv_HOST.host_run_command("hwclock --hctosys;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the system time from hwclock failed")

    ##
    # @brief This function keeps hwclock in UTC format.
    def hwclock_in_utc(self):
        print "Keeping the hwclock in UTC format"
        l_res = self.cv_HOST.host_run_command("hwclock --utc;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Keeping the hwclock in UTC is failed")

    ##
    # @brief This function keeps hwclock in local time format.
    def hwclock_in_localtime(self):
        print "Keeping the hwclock in localtime"
        l_res = self.cv_HOST.host_run_command("hwclock --localtime;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Keeping the hwclock in localtime is failed")

    ##
    # @brief This function tests hwclock compare functionality for a time of 100 seconds.
    #        Here checking the return status of timeout as 124, if compare works fine. any
    #        other return value means compare function failed.
    def hwclock_compare(self):
        print "Testing hwclock compare functionality for a time of 10 seconds"
        l_res = self.cv_HOST.host_run_command("timeout 10 hwclock --compare; echo $?")
        l_res = l_res.splitlines()
        print l_res
        self.assertEqual(int(l_res[-1]), 124, "hwclock compare function failed")

    ##
    # @brief This function predict RTC reading at time given with --date
    #
    # @param i_time @type string: time at which predict hwclock reading
    def hwclock_predict(self, i_time):
        print "Testing the hwclock predict function to a time: %s" % i_time
        l_res = self.cv_HOST.host_run_command("hwclock --predict --date \'%s\';echo $?" % i_time)
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "hwclock predict function failed")

    ##
    # @brief This function tests hwclock debug mode.
    #        In this mode setting hwclock from system time
    #        and setting system time from hwclock
    def hwclock_debug_mode(self):
        print "Testing the hwclock debug mode"
        l_res = self.cv_HOST.host_run_command("hwclock --systohc --debug;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the hwclock from system time in debug mode failed")
        l_res = self.cv_HOST.host_run_command("hwclock --hctosys --debug;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "Setting the system time from hwclock in debug mode failed")

    ##
    # @brief This function tests the hwclock test mode. In this mode setting the hwclock
    #        time using --set option. Here it just execute but should not set hwclock time.
    #
    # @param i_time @type string: time to set hwclock in test mode
    def hwclock_test_mode(self, i_time):
        print "Testing the hwclock test mode, set time to: %s" % i_time
        l_res = self.cv_HOST.host_run_command("hwclock --set --date \'%s\' --test;echo $?" % i_time)
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "hwclock test function failed")

    ##
    # @brief This function tests hwclock adjust functionality
    def hwclock_adjust(self):
        print "Testing the hwclock adjust function"
        l_res = self.cv_HOST.host_run_command("hwclock --adjust;echo $?")
        l_res = l_res.splitlines()
        self.assertEqual(int(l_res[-1]), 0, "hwclock adjust function failed")
        l_res = self.cv_HOST.host_run_command("cat /etc/adjtime")
