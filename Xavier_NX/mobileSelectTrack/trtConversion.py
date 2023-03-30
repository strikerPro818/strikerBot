import torch
import torchreid
import tensorrt as trt

# Load pre-trained OSNet model with x0.25 width multiplier
model_name = 'osnet_x0_25'
model = torchreid.models.build_model(
    name=model_name,
    num_classes=1000,
    pretrained=True
)

# Create example input tensor
data_shape = (3, 256, 128)
input_tensor = torch.randn(1, *data_shape)

# Build TensorRT engine
engine_file_path = f'{model_name}.engine'
with trt.Logger(trt.Logger.INFO) as logger:
    with trt.Builder(logger) as builder, builder.create_network() as network:
        # Configure builder
        config = builder.create_builder_config()
        config.max_workspace_size = 1 << 30  # 1 GB
        builder.max_batch_size = 1

        # Create input tensor
        input_tensor_trt = network.add_input(
            name='input',
            dtype=trt.float32,
            shape=(3, 256, 128)
        )

        # Convert PyTorch model to TensorRT engine
        model_trt = torchreid.engine.build_engine(
            model=model,
            data_shape=data_shape,
            fp16_mode=True,
            engine_file_path=engine_file_path,
            builder=builder,
            config=config
        )

        # Create output tensor
        output_tensor_trt = model_trt(input_tensor_trt)

        # Add output tensor to network
        network.mark_output(
            name='output',
            tensor=output_tensor_trt
        )

        # Build engine
        engine = builder.build_cuda_engine(network)

        # Save engine
        with open(engine_file_path, 'wb') as f:
            f.write(engine.serialize())
