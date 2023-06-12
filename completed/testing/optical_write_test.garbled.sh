    mkdir -p $TEMP_DIR || return 1
    cd $TEMP_DIR || return 1
    cp -a $SAMPLE_FILE_PATH/$SAMPLE_FILE $TEMP_DIR
    md5sum -- * > $TEMP_DIR/$MD5SUM_FILE
    check_md5 $TEMP_DIR/$MD5SUM_FILE
    md5sum -c "$1"
    genisoimage -input-charset UTF-8 -r -J -o $ISO_NAME $SAMPLE_FILE
    sleep 10
        wodim -eject dev="$OPTICAL_DRIVE" $ISO_NAME
        growisofs -dvd-compat -Z "$OPTICAL_DRIVE=$ISO_NAME"

        sleep $INTERVAL

        mount "$OPTICAL_DRIVE" 2>&1 | \
            grep -E -q "already mounted"
    rm -rf $SAMPLE_FILE
    mount
    grep -q "$OPTICAL_DRIVE"
        mount
        grep "$OPTICAL_DRIVE"
        awk '{print $3}')
        mount "$OPTICAL_DRIVE" $MOUNT_PT
    cp $MOUNT_PT/* $TEMP_DIR
    check_md5 $MD5SUM_FILE
    cd "$START_DIR" || exit 1
    umount "$MOUNT_PT"
    rm -fr $TEMP_DIR
    eject "$OPTICAL_DRIVE"
    cleanup
    readlink -f "$1")
