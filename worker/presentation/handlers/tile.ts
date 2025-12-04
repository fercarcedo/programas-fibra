import type { IRequest } from "itty-router";
import type { TileService } from "../../application/services/tile_service";

export interface GetTileRouterRequest extends IRequest {
  params: {
    tileName: string;
    z: string;
    x: string;
    y: string;
  };
}

export async function getTile(request: GetTileRouterRequest, tileService: TileService) {
  const { tileName, z, x, y } = request.params;

  const tileX = parseInt(x);
  const tileY = parseInt(y);
  const tileZ = parseInt(z);

  if (isNaN(tileX) || isNaN(tileY) || isNaN(tileZ)) {
    return new Response(null, { status: 400 });
  }
  
  const tileData = await tileService.getTile(tileName, tileX, tileY, tileZ);

  if (!tileData) {
    console.warn(`Tile data not found for tile: ${tileName} and coordinates ${tileX},${tileY},${tileZ}`);
    return new Response(new Uint8Array(0), {
      status: 200,
      headers: {
        'Content-Type': 'application/x-protobuf',
        'Cache-Control': 'public, max-age=3600',
      },
    });
  }

  return new Response(tileData, {
    headers: {
      'content-type': 'application/x-protobuf',
      'cache-control': 'public, max-age=31536000, immutable',
    },
  });
}