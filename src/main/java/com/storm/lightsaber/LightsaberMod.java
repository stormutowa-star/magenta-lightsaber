package com.storm.lightsaber;

import com.mojang.logging.LogUtils;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/**
 * Magenta Lightsaber - a gold-and-silver hilt with a blazing magenta plasma blade.
 */
@Mod(LightsaberMod.MODID)
public class LightsaberMod {
    public static final String MODID = "magenta_lightsaber";
    public static final Logger LOGGER = LogUtils.getLogger();

    public LightsaberMod(FMLJavaModLoadingContext context) {
        IEventBus modBus = context.getModEventBus();
        ModDataComponents.register(modBus);
        ModItems.register(modBus);
        LOGGER.info("Loading Magenta Lightsaber");
    }
}
