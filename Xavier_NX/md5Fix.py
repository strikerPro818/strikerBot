import h5py
filepath = "/home/striker/Jetson/Xavier_NX/resnet50-0676ba61.pth"
if h5py.is_hdf5("/home/striker/Jetson/Xavier_NX/resnet50-0676ba61.pth"):
    print('yes')
    # file is a valid HDF5 file
else:
    print('fuck')
    # file is not a valid HDF5 file

with h5py.File(filepath, 'r') as f_in, h5py.File('output.pth', 'w') as f_out:
    f_out.copy(f_in, compression='gzip', compression_opts=9)