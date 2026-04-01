export const GAME_TYPE_TO_ITEM_TYPE_ID = {
} as const;

export type GameType = keyof typeof GAME_TYPE_TO_ITEM_TYPE_ID;
