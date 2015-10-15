import socket
from struct import pack, unpack
from .tracker import Marker, MarkerSet, RigidBody
from cStringIO import StringIO
import time
import threading
import warnings
import datetime

def strcpy(stream):
    """Reads a IOStream one step at a time, returning the previous string before it reached a null character."""
    eof, szName, idx = '', [], 0
    while idx <= 200 and eof != '\x00':  # Read until null terminator or after 200 characters.
        szName.append(eof)
        eof = stream.read(1)
    return ''.join(szName).replace(' ', '_')  # Convert to string without spaces.

NAT_PING  					= 0
NAT_PINGRESPONSE			= 1
NAT_REQUEST					= 2
NAT_RESPONSE				= 3
NAT_REQUEST_MODELDEF		= 4
NAT_MODELDEF				= 5
NAT_REQUEST_FRAMEOFDATA		= 6
NAT_FRAMEOFDATA				= 7
NAT_MESSAGESTRING			= 8
NAT_UNNRECOGNIZED_REQUEST	= 100
UNDEFINED					= 999999.9999

MAX_PACKETSIZE				= 100000
MAX_NAMELENGTH				= 256

CLIENT_ADDRESS =            "127.0.0.1" #socket.gethostbyname(socket.gethostname())  #Default is now local address.
MULTICAST_ADDRESS			= "239.255.42.99"
PORT_COMMAND				= 1510
PORT_DATA					= 1511

OPT_VAL						= 0x100000


class NatBaseError(Exception):
    pass


class NatUnrecognizedRequest(NatBaseError):
    def __init__(self, message):
        print(message)


class NatServerMessageError(NatBaseError):
    def __init__(self, message):
        print(message)


class NatPacket(object):

    def __init__(self, packet):
        self.iMessage, self.nDataBytes = unpack('HH', packet[:4])  # Message ID, then Number of Bytes in Payload.
        self._packet = packet

class NatSocket(object):

    def __init__(self, client_ip, port, max_packet_size=MAX_PACKETSIZE):

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.client_ip = client_ip
        self.port = port
        # self.port = socket.htons(uPort)  # Not sure why this is necessary.
        assert isinstance(max_packet_size/4, int), "max_packet_size must be divisible by 4"
        self.max_packet_size = max_packet_size

class NatCommSocket(NatSocket):

    def __init__(self, client_ip=CLIENT_ADDRESS, uPort=PORT_COMMAND,
                 max_packet_size=MAX_PACKETSIZE):
        """Internet Protocol socket with presets for Motive Command Socket.

        Args:
            client_ip (int): an int

        """
        super(NatCommSocket, self).__init__(client_ip, uPort, max_packet_size)
        # Set Instance Attributes
        self.server_ip = client_ip  # Currently set to same value as client_ip.  May change when computer changes.

        # Connect Socket
        self._sock.bind((client_ip, 0))
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.setblocking(0)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, OPT_VAL)  # Not originally in this function. Check why.

    def recv(self):
        """Receives packet from NatNet Server and returns as NatPacket instance."""
        packet = self._sock.recv(self.max_packet_size + 4)
        packet = NatPacket(packet)
        print( "[Client] Received command from {0}: Command={1}, nDataBytes={2}".format(
                self.client_ip, packet.iMessage, packet.nDataBytes))
        return packet

    def send(self, nat_value, message='', sleep_time=.02):
        """
        Send an integer command to NatNet Server, usually as a request for some packet type on the command socket.

        .. note:: Values Available, along with value to expect in NatPacket.iMessage when receiving the response:
          - 0 = NAT_PING
          - 1 = NAT_PINGRESPONSE
          - 2 = NAT_REQUEST  (must also send a message string.)
          3 = NAT_RESPONSE
          4 = NAT_REQUEST_MODELDEF		
          5 = NAT_MODELDEF
          6 = NAT_REQUEST_FRAMEOFDATA
          7 = NAT_FRAMEOFDATA
          8 = NAT_MESSAGESTRIN
        
        """
        message_len = len(message)

        if message_len > 0:
            self._sock.sendto(pack("HH"+str(message_len)+"s", nat_value, 4+message_len, message), (self.server_ip, self.port))  # send both nat_value and packet size
        else:
            self._sock.sendto(pack("HH", nat_value, 4), (self.server_ip, self.port))  # send both nat_value and packet size

        time.sleep(sleep_time)
        print("Message sent.")

    def get_data(self, nat_value, message='', num_attempts=3):
        """Combines the send() and recv() functions into a single convenience function for requesting data.
        Does multiple attempts and confirms that received packet is the type that was requested. Returns NatPacket."""

        packet = None
        for send_attempt in range(num_attempts):
            self.send(nat_value, message)

            for receive_attempt in range(num_attempts):
                time.sleep(.008)
                packet = self.recv()
                if packet.iMessage == nat_value + 1:
                    print("Correct packet received on attempt {0}.".format(receive_attempt))
                    # if packet.iMessage == NAT_RESPONSE:  # Should always get a reply, but seems a bit unreliable.
                    #    print("Message: {0}".format(packet._packet[4:]))
                    return packet

        # If the correct packet wasn't received, return an error, depending on what happened.
        if isinstance(packet, NatPacket):
            if packet.iMessage == NAT_UNNRECOGNIZED_REQUEST:
                raise NatUnrecognizedRequest("Server does not recognize the command.")
            elif packet.iMessage == NAT_MESSAGESTRING:
                raise NatServerMessageError(packet._packet[4:])
        else:
            raise NatBaseError("Did not receive any NatPackets.")


class NatDataSocket(NatSocket):

    def __init__(self, client_ip=CLIENT_ADDRESS, port=PORT_DATA, max_packet_size=MAX_PACKETSIZE):
        """Internet Protocol socket with presets for Motive Data Socket."""
        super(NatDataSocket, self).__init__(client_ip, port, max_packet_size)

        # Configure and Connect socket
        self._sock._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = socket.inet_aton(MULTICAST_ADDRESS) + socket.inet_aton(client_ip)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, OPT_VAL)
        self._sock.bind((client_ip, port))
        # self.bind((Optitrack.CLIENT_ADDRESS, socket.htons(Optitrack.PORT_DATA)))  # If the above line doesn't work.
        self._sock.settimeout(4.0)

    def recv(self):
        """Receives packet from NatNet Server and returns as NatPacket instance."""
        return NatPacket(self._sock.recv(self.max_packet_size))


class Optitrack(object):

    def __init__(self, client_ip=CLIENT_ADDRESS, data_port=PORT_DATA, comm_port=PORT_COMMAND, read_rate=400):
        """
        The Optitrack NatNet Interface.  When initialized, starts a background thread that automatically updates data.

        The Optitrack object is the main object for acquiring 3D marker data from the Motive NatNet Streaming.  It uses their depaketezation example to parse the data packet, and it does so in a background thread.  :py:class:`.NatDataSocket` and :py:class:`.NatCommSocket` are automatically created and wrapped by the Optitrack object, and several other convenence functions have been added.

        Args:
            client_ip (str): The Motive server ip address.  If running on the same PC as Motive, both IP settings should be set to 'Local Loopback', which is '127.0.0.1'.  
            data_port (int): The NatNet Data Socket port number.  Should match the settings in the Streaming pane in Motive.
            comm_port (int): The NatNet Command Socket port number.  Should match the settings in the Streaming pane in Motive.
            read_rate (int): How often the thread should loop, in frames per second.  Should be set faster than the camera framerate, or the data acquired will be laggy as the buffer fills.
        """

        # Initialize data structures
        #: A list of Markers that are unassociated with a RigidBody.
        self.unidentified_markers = []
        self.labeled_markers = dict()
        #self.labeled_markers = dict()  # Removed because of non-uniqueness of id and duplication of data. Now, labeled marker data goes into rigid body markers.
        self.marker_sets = dict()
        self.rigid_bodies_by_id = dict()
        self.rigid_bodies = dict()

        self.iFrame = None
        self.latency = None
        self.time = None
        self.timestamp = None

        self._is_recording = False
        self.recording_start_time = 0
        self.tracked_models_changed = True

        # Create Command and Data Sockets
        self.comm_sock = NatCommSocket(client_ip, comm_port)

        # Ping server to establish connection and get version numbers.
        self.server_name, self.version, self.natnet_version = self.ping()

        # Get model definitions
        self.get_model()

        # Connect up data socket to get packet data, and then start a continuous reader thread to keep data up-to-date.
        self.data_sock = NatDataSocket(client_ip=client_ip, port=data_port)
        self._data_thread = threading.Thread(group=None, target=self._continuous_get_data, name="Optitrack Reader Thread", args=(1./read_rate, ))
        self._data_thread.daemon = True
        self._data_thread.start()

        # Get first frame of data, and check to make sure no recordings are already in progress.
        self.get_data()

        #assert not self.is_recording, "Motive is already recording!  Please stop recording and reconnect to continue."


    @property
    def timestamp_recording(self):
        return self.timestamp - self.recording_start_time if self.is_recording else 0.

    @property
    def is_recording(self):
        return self._is_recording

    @is_recording.setter
    def is_recording(self, bool_value):
        if bool_value == True and self._is_recording == False:
            self.recording_start_time = self.timestamp
        self._is_recording = bool_value

    def ping(self):
        """Sends initial Ping command to Motive to begin receiving data and alert Motive to our presence.
        Returns tuple: (server_name, Version, NatNetVersion)"""

        packet = self.comm_sock.get_data(NAT_PING)

        unpacked = unpack(str(MAX_NAMELENGTH) + "s4B4B", packet._packet[4:])
        server_name = unpacked[0].split('\x00')[0]  # Rest of name string is junk.
        Version = unpacked[1:5]
        NatNetVersion = unpacked[5:9]

        assert NatNetVersion[0] >= 2, "NatNetVersion not compatible with parser (Requires 2.0.0.0 or up)"
        print('Ping Response Received from compatible server.')

        return (server_name, Version, NatNetVersion)

    def set_take_file_name(self, file_name):
        if self.is_recording:
            raise IOError("Cannot change Motive Take filename if already recording.")

        warnings.warn("WARNING: Changing the Take File Name often results in Motive Crashing and Faulting...\n...best to not "
                          "use this functionality for current_time.  Trying anyway...")
        self.comm_sock.send(2, "SetRecordTakeName," + file_name)

    def start_recording(self, n_attempts=3):
        """
        Sends the 'StartRecording' command over the NatNet Command Port to Motive.

        Args:
            n_attempts (int): How many times to attempt before raising a RunTimeError
        """

        # Make sure that a recording hasn't already begun, by checking data on Data Port.
        self.get_data()
        if self.is_recording:
            raise RuntimeError("Cannot Start New Recording, as recording is already in progress.")

        # Send "StartRecording" command to NatNet via a NATREQUEST command
        for attempt in range(n_attempts):
            # Using comm_sock.get_data() sometimes gets annoying non-blocking error.
            self.comm_sock.send(2, "StartRecording")
                
            # Check if successful, by getting new data packet.
            self.get_data()
            if self.is_recording:
                break
        else:    
            raise RuntimeError("Recording failed after {0} attempts.".format(attempt))

    def stop_recording(self, n_attempts=3):
        """
        Sends the 'StopRecording' command over the NatNet Command Port to Motive. 

        .. warning:: This method isn't working at the moment, for reasons not yet uncovered.  Still, will raise an error if unsuccessful, so this method is safe to test on your system.

        Args:
            n_attempts (int): Number of times to attempt before raising a RunTimeError.

        Raises:
            RuntimeError: If recording is already stopped when called, or if fails to stop after being called.

        """
        self.get_data()
        if self.is_recording == False:
            raise NatBaseError("Cannot Stop Recording, as no recording is currently happening!")

        # Send "StartRecording" command to NatNet via a NATREQUEST command
        for attempt in range(n_attempts):
            self.comm_sock.send(2, "StopRecording")  # Using comm_sock.get_data sometimes gets annoying non-blocking error.

            # Check if successful, by getting new data packet.
            self.get_data()
            if self.is_recording == False:
                print("Recording Started Successfully")
                return
            else:
                print("Recording failed on attempt number {0}.  Trying again...".format(attempt))

        warnings.warn("Motive isn't currently responding to the 'StopRecording' command.  This seems to be a Motive bug, but cause is unknown.\n"
                      "For the time being, manual stopping is suggested.")
        raise NatBaseError("Recording Not Stopped Successfully, for unknown reasons.")

    def get_model(self):

        # Receive ModelDef NatPacket
        try:
            packet = self.comm_sock.get_data(NAT_REQUEST_MODELDEF)
        except NatUnrecognizedRequest:
            print("Warning: Server Doesn't recognize request for Modeldef.  Will try again after next frame...")
            return None

        # Parse the Packet
        data = StringIO(packet._packet[4:]) # Skip Message ID, nBytes data

        d_name_list = []
        for el in range(unpack('i', data.read(4))[0]):  # nDatasets
            d_type = unpack('i', data.read(4))[0]
            d_name = strcpy(data)
            d_name_list.append(d_name)

            # MarkerSet
            if d_type == 0:
                if not d_name in self.marker_sets:
                    self.marker_sets[d_name] = MarkerSet(name=d_name)
                marker_set = self.marker_sets[d_name]
                nMarkers = unpack('i', data.read(4))[0]
                if len(marker_set.markers) != nMarkers:
                    marker_set.markers = []
                    for el2 in range(nMarkers):
                        name = strcpy(data)
                        marker_set.markers.append(Marker(name=name))
                else:
                    for el2 in range(nMarkers):  # nMarkers
                        name = strcpy(data)
                        marker_set.markers[el2].name = name

            # Rigid Body
            elif d_type == 1:
                id, parent_id, x_offset, y_offset, z_offset = unpack('2i3f', data.read(20))
                if not d_name in self.rigid_bodies:
                    body = RigidBody(name=d_name, id=id, parent_id=parent_id, offset=(x_offset, y_offset, z_offset))
                    self.rigid_bodies[d_name], self.rigid_bodies_by_id[id] = body, body

            # Skeleton
            elif d_type == 2:
                raise NotImplementedError("Skeleton Processing not yet implemented! Remove them from Motive Tracking!")  # TODO: Get skeletons working.
                """
                id = unpack('2i', data.read(4))[0]
                skeleton = Skeleton(id=id, name=d_name)

                for el2 in range(unpack('2i', data.read(4))[0]):  # nRigidBodies
                    name = strcpy()(data)
                    id, parent_id, x_offset, y_offset, z_offset = unpack('2i3f', data.read(20))
                    body = RigidBody(id=id, name=name, offset=(x_offset, y_offset, z_offset))
                    skeleton.rigid_bodies[name] = body
                    skeleton.rigid_bodies[id] = body
                skeletons[d_name] = skeleton
                skeletons[id] = skeleton
                """

        # Now, delete any items from the dictionaries that aren't in the server's model.
        for dictionary in [self.marker_sets, self.rigid_bodies]:
            for name in dictionary.keys():
                if name not in d_name_list:
                    del dictionary[name]

        return packet

    def _continuous_get_data(self, sleep_time):
        while True:
            time.sleep(sleep_time)
            self.get_data()

    def get_data(self):
        """Update Position data with NatPacket containing Frame data."""

        # TODO: Set up auto-detection of changes in the models, so that self.get_model() gets called.

        try:
            major = self.natnet_version[0]
            minor = self.natnet_version[1]
        except KeyError:
            raise KeyError("Can't get data until NatNetVersion is known. Try re-pinging the server.")

        packet = self.data_sock.recv()

        # Get Data and Convert to StringIO type for easier and quicker reading.
        data = StringIO(packet._packet[4:])

        # Frame Number
        self.iFrame = unpack("i", data.read(4))[0]  # Frame number

        # MarkerSets
        nMarkerSets = unpack("i", data.read(4))[0]
        for el in range(nMarkerSets):  # nMarkerSets
            marker_set = self.marker_sets[strcpy(data)]  # Get name of markerset
            nMarkers = unpack('i', data.read(4))[0]
            assert nMarkers == len(marker_set.markers)
            for marker in marker_set.markers:  # nMarkers
                marker.position = unpack('3f', data.read(12))

        # Unidentified Markers
        self.unidentified_markers = []
        nOtherMarkers = unpack('i', data.read(4))[0]
        for el in range(nOtherMarkers):  # nOtherMarkers
            x, y, z = unpack('3f', data.read(12))
            self.unidentified_markers.append(Marker(position=(x, y, z)))  # (x, y, z)

        # Rigid Bodies
        nRigidBodies = unpack('i', data.read(4))[0]
        for el in range(nRigidBodies):  # nRigidBodies
            # Get body id, position, and rotation
            body_id, x, y, z, qx, qy, qz, qw = unpack('i7f',data.read(32))
            body = self.rigid_bodies_by_id[body_id] #self.rigid_bodies[id]
            body.position = x, y, z
            body.rotation = qx, qy, qz, qw

            # Get body's markers' information
            body.markers = []  # That's right.  Reset the whole damn marker list.
            for el2 in range(unpack('i', data.read(4))[0]):  # nRigidMarkers
                mx, my, mz = unpack('3f', data.read(12))
                body.markers.append(Marker(position=(mx, my, mz)))

            for mark_idx in range(len(body.markers)):  # Works for NatNet 2.0.0.0 on.
                body.markers[mark_idx].id = unpack('i', data.read(4))[0]  # Marker ID
            for mark_idx in range(len(body.markers)):
                body.markers[mark_idx].size = unpack('f', data.read(4))[0]  # Defaults to 24mm, unless "Diameter Calculation" is checked in Motive's Reconstruction pane.

            # Get other info about body recording.
            body.error = unpack('f', data.read(4))  # Mean marker error (in meters/marker)
            if (major == 2 and minor >= 6) or major > 2:
                body.seen = bool(unpack('h', data.read(2))[0] & 0x01)  # Tracking was successful (bTrackingValid)


        # Skeletons (version 2.1 and later)
        if (major == 2 and minor > 0) or major > 2:

            nSkeletons = unpack('i', data.read(4))[0]

            # TODO: Get Skeletons working.
            if nSkeletons is not 0:
                raise NotImplementedError("Skeletons in dataset. This functionality is not yet tested.")
            """    self.skeletons = dict()

            for el in range(nSkeletons):  # nSkeletons

                skel_id = unpack('i', data.read(4))[0]
                skeleton = self.skeletons[skel_id]
                for el2 in range(unpack('i', data.read(4))[0]):  # nRigidBodies

                    body_id, x, y, z, qx, qy, qz, qw = unpack('i7f',data.read(32))
                    body = skeleton.rigid_bodies[body_id]
                    body.position, body.rotation = (x, y, z), (qx, qy, qz, qw)

                    body.markers = []  # That's right.  Reset the whole damn marker list.
                    for el3 in range(unpack('i', data.read(4))[0]):  # nRigidMarkers
                        x, y, z = unpack('3f', data.read(12))
                        body.markers.append(Marker((x, y, z)))
                    for mark_idx in range(len(body.markers)):
                        body.markers[mark_idx].id = unpack('i', data.read(4))[0]  # Marker ID
                    for mark_idx in range(len(body.markers)):
                        body.markers[mark_idx].size = unpack('f', data.read(4))[0]

                    body.error = unpack('f', data.read(4))[0]  # Mean marker error (fError)
                    skeleton.rigid_bodies.append(body)
            """

        # Labeled Markers (version 2.3 and later).  IDs are not unique to marker, just within each body.  Apply to body accordingly.
        if (major == 2 and minor >= 3) or major > 2:
            nLabeledMarkers = unpack('i', data.read(4))[0]

            for el in range(nLabeledMarkers):  # nLabeledMarkers
                marker_id, x, y, z, size = unpack('i4f', data.read(20))
                if marker_id in self.labeled_markers:
                    self.labeled_markers[marker_id].position = x, y, z
                    self.labeled_markers[marker_id].size = size
                else:
                    labeled_marker = Marker(position=(x, y, z))
                    labeled_marker.id = marker_id
                    labeled_marker.size = size
                    self.labeled_markers[marker_id] = labeled_marker

                # (version 2.6 and later)
                if (major == 2 and minor >= 6) or major > 2 or major == 0:
                    params = unpack('h', data.read(2))[0]
                    self.labeled_markers[marker_id].occluded = bool(params & 0x01)  # marker occluded this frame
                    self.labeled_markers[marker_id].pc_solved = bool(params & 0x02)  # Position provided by point cloud solve (directly measured)
                    self.labeled_markers[marker_id].model_solved = bool(params & 0x04)  # Position provided by model solve (indirectly filled in)

        # Final Frame Info
        self.latency = unpack('f', data.read(4))[0]  # TODO: Find out how Optitrack latency is calculated. Somehow related to self.timestamp.
        (timecode, timecodeSub) = unpack('2I', data.read(8))  # TODO: Get timecode.  Seems stuck at 0:0:0:0.0
        hours = timecode // (60 * 60)
        minutes = (timecode - (hours * 360)) // 60
        seconds = timecode % 60
        sub_frames = timecodeSub
        self.time = datetime.time(hours, minutes, seconds)  # TODO: Encode sub_frames into timecode.

        if (major == 2 and minor >= 7) or major > 2:
            self.timestamp = unpack('d', data.read(8))[0]  # Seconds since starting session, in Double Precision Float
        else:
            self.timestamp = unpack('f', data.read(4))[0]  # Seconds since starting session, in Float

        # Check if models have changed from last frame (perhaps something was added during recording session.)
        end_params = unpack('h', data.read(2))[0]
        self.is_recording = bool(end_params & 0x01)  # Motive is Recording
        self.tracked_models_changed = bool( end_params & 0x02)

    def wait_for_recording_start(self):
        """Halts script until recording begins."""
        print("Waiting for recording to begin...")
        while not self.is_recording:
            self.get_data()
        print("...Recording started.")

    def wait_for_recording_stop(self):
        """Halts script until recording ends."""
        print("Waiting for recording to end...")
        while self.is_recording:
            self.get_data()
        print("...Recording stopped.")


