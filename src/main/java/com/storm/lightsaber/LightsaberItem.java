package com.storm.lightsaber;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

public class LightsaberItem extends Item {
    private static final ResourceLocation DAMAGE_ID =
            ResourceLocation.fromNamespaceAndPath(LightsaberMod.MODID, "active_attack_damage");
    private static final ResourceLocation SPEED_ID =
            ResourceLocation.fromNamespaceAndPath(LightsaberMod.MODID, "active_attack_speed");

    private static final ItemAttributeModifiers ACTIVE_MODIFIERS = ItemAttributeModifiers.builder()
            .add(Attributes.ATTACK_DAMAGE, new AttributeModifier(
                    DAMAGE_ID, 8.0D, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ATTACK_SPEED, new AttributeModifier(
                    SPEED_ID, -2.4D, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .build();

    public LightsaberItem(Properties properties) {
        super(properties);
    }

    public static boolean isActive(ItemStack stack) {
        return Boolean.TRUE.equals(stack.get(ModDataComponents.ACTIVE.get()));
    }

    public static void setActive(ItemStack stack, boolean active) {
        if (active) {
            stack.set(ModDataComponents.ACTIVE.get(), Boolean.TRUE);
            stack.set(DataComponents.ATTRIBUTE_MODIFIERS, ACTIVE_MODIFIERS);
        } else {
            stack.remove(ModDataComponents.ACTIVE.get());
            stack.remove(DataComponents.ATTRIBUTE_MODIFIERS);
        }
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean activate = !isActive(stack);
        setActive(stack, activate);

        if (!level.isClientSide) {
            playIgnitionSound(level, player, activate);
            if (activate) {
                spawnIgnitionParticles(player);
            }
        }

        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    private static void playIgnitionSound(Level level, Player player, boolean activate) {
        double x = player.getX();
        double y = player.getY() + 1.0D;
        double z = player.getZ();

        if (activate) {
            level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 0.75F, 1.85F);
            level.playSound(null, x, y, z, SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 0.85F, 1.55F);
        } else {
            level.playSound(null, x, y, z, SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 0.8F, 1.45F);
            level.playSound(null, x, y, z, SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 0.9F, 1.1F);
        }
    }

    private static void spawnIgnitionParticles(Player player) {
        if (!(player.level() instanceof ServerLevel serverLevel)) {
            return;
        }

        Vec3 look = player.getLookAngle();
        double x = player.getX() + look.x * 0.45D;
        double y = player.getY() + 1.15D + look.y * 0.25D;
        double z = player.getZ() + look.z * 0.45D;

        serverLevel.sendParticles(
                new DustParticleOptions(new Vector3f(1.0F, 0.18F, 1.0F), 1.15F),
                x, y, z, 18, 0.18D, 0.18D, 0.18D, 0.02D);
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        if (isActive(stack) && !attacker.level().isClientSide) {
            Level level = attacker.level();
            level.playSound(null, target.getX(), target.getY() + target.getBbHeight() * 0.5D, target.getZ(),
                    SoundEvents.TRIDENT_HIT, SoundSource.PLAYERS, 0.55F, 1.55F);

            if (level instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(
                        new DustParticleOptions(new Vector3f(1.0F, 0.12F, 1.0F), 0.9F),
                        target.getX(), target.getY() + target.getBbHeight() * 0.5D, target.getZ(),
                        8, 0.22D, 0.22D, 0.22D, 0.02D);
            }
        }
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        boolean active = isActive(stack);
        tooltip.add(Component.translatable("tooltip.magenta_lightsaber.state",
                        Component.translatable(active
                                        ? "tooltip.magenta_lightsaber.on"
                                        : "tooltip.magenta_lightsaber.off")
                                .withStyle(active ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.DARK_GRAY))
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.magenta_lightsaber.hint")
                .withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
        super.appendHoverText(stack, context, tooltip, flag);
    }
}
