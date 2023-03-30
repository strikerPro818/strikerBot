import sys
import gi
import os
os.environ['LD_LIBRARY_PATH'] += ':/usr/local/deepstream/deepstream/lib/'
os.environ['PATH'] += ':/usr/local/deepstream/deepstream/bin'


gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, GstBase, GstApp, GstVideo

# Initialize GObject and GStreamer
GObject.threads_init()
Gst.init(None)

# Define the pipeline configuration
pipeline = """
    nvstreammux name=mux batch-size=1 width=640 height=480 ! 
    nvdsosd ! nvtracker tracker-width=640 tracker-height=480 ! 
    nvvideoconvert ! video/x-raw, format=BGRx ! 
    nvinfer config-file-path=yolov5_config.txt ! nvvideoconvert ! 
    video/x-raw(memory:NVMM), format=NV12 ! nvoverlaysink sync=false
"""

# Create the pipeline
pipe = Gst.parse_launch(pipeline)

# Start the pipeline
pipe.set_state(Gst.State.PLAYING)

# Wait for the pipeline to start up
bus = pipe.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.STATE_CHANGED)
while msg.src != pipe:
    msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.STATE_CHANGED)

# Set up the object tracker
tracker = pipe.get_by_name('nvtracker')
tracker.set_property('ll-lib-file', '/opt/nvidia/deepstream/deepstream-5.0/lib/libnvds_nvdcf.so')
tracker.set_property('tracker-width', 640)
tracker.set_property('tracker-height', 480)

# Define a dictionary to store object IDs
object_ids = {}

# Listen for object detection events
sink = pipe.get_by_name('mux')
sink.connect('element-added', on_element_added)


def on_element_added(sink, element):
    if isinstance(element, GstBase.GenericVideoSink):
        element.connect('handoff', on_object_detected)


def on_object_detected(sink, buffer, pad, obj):
    # Get the bounding box of the detected object
    bbox = obj.meta['nvds_bbox']
    x1 = bbox.left
    y1 = bbox.top
    x2 = bbox.left + bbox.width
    y2 = bbox.top + bbox.height

    # Assign an ID to the person
    if obj.label == 'person':
        if obj.object_id not in object_ids:
            object_ids[obj.object_id] = len(object_ids) + 1
        person_id = object_ids[obj.object_id]
        print(f'Detected person {person_id} at ({x1}, {y1}) - ({x2}, {y2})')
    else:
        print(f'Detected object of type {obj.label} at ({x1}, {y1}) - ({x2}, {y2})')


# Run the pipeline until terminated
try:
    loop = GObject.MainLoop()
    loop.run()
except KeyboardInterrupt:
    pass

# Stop and clean up the pipeline
pipe.set_state(Gst.State.NULL)
