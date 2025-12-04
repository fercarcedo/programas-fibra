import { Buffer } from 'buffer';
import * as zlib from 'zlib';
import Pbf from 'pbf';

/**
 * Creates a mock MVT data buffer for testing.
 * This example encodes a single point feature in a "roads" layer.
 * @returns A Gzip-compressed MVT buffer (simulating the raw file content).
 */
export function createMockMvtBuffer(): Buffer {
  // --- 1. Protobuf Encoding (Manual or using a library helper) ---
  
  const pbf = new Pbf();
  
  // MVT Structure (Simplified)
  // Message Tile = 3
  pbf.writeVarintField(3, (tilePbf) => { 
    // Layer 1: "roads" layer
    // tag 1: name = "roads"
    tilePbf.writeStringField(1, 'roads'); 
    
    // tag 2: features
    tilePbf.writeMessage(2, (layerPbf) => { 
      // Feature 1
      layerPbf.writeMessage(2, (featurePbf) => {
        // tag 1: id = 123
        featurePbf.writeVarintField(1, 123); 
        // tag 3: geometry type (Point = 1)
        featurePbf.writeVarintField(3, 1);
        // tag 4: geometry (Protobuf-encoded coordinates)
        // Commands: MoveTo(0) + X(10) + Y(20) -> [9, 20, 40]
        featurePbf.writePackedVarint(4, [9, 20, 40]); 
        
        // tag 2: attributes (key/value pairs)
        featurePbf.writePackedVarint(2, [
            0, // key index 0 (name)
            0  // value index 0 ("Main Street")
        ]);
      });
      
      // tag 3: keys (string pool for attribute keys)
      layerPbf.writeStringField(3, 'name'); 
      // tag 4: values (string pool for attribute values)
      layerPbf.writeStringField(4, 'Main Street');
      // tag 5: extent = 4096 (default)
      layerPbf.writeVarintField(5, 4096); 
      // tag 15: version = 2 (latest)
      layerPbf.writeVarintField(15, 2); 
    });
  });

  const protobufBuffer = pbf.finish();

  // --- 2. Gzip Compression ---
  
  // Use zlib.gzipSync for synchronous operation in tests
  const gzippedBuffer = zlib.gzipSync(protobufBuffer);
  
  return gzippedBuffer;
}