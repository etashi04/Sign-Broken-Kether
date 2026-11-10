# Korean title textures use their own glyph mask for fire; Chinese/Japanese fields cannot leave glyph-shaped fire remnants.


init python early:
    renpy.register_shader("ko.p10_spear_title_clamp", variables="""
    uniform sampler2D tex0;
    uniform sampler2D tex1;
    uniform float u_p10title_time;
    attribute vec2 a_tex_coord;
    varying vec2 v_p10title_uv;
""", vertex_300="v_p10title_uv = a_tex_coord;", fragment_functions="""
    float p10title_ease(float x) {
        x = clamp(x, 0.0, 1.0);
        return x*x*(3.0-2.0*x);
    }
    float p10title_seam_sample(float x) {
        return 740.0 + 5.0*sin(x*0.027) + 3.0*sin(x*0.093) + 2.0*sin(x*0.171);
    }
    float p10title_seam(float x) {
        float cell = floor(x/8.0)*8.0;
        return mix(p10title_seam_sample(cell), p10title_seam_sample(cell+8.0), fract(x/8.0));
    }
    float p10title_piece(sampler2D glyph, sampler2D burn_field, vec2 src, float side, float t) {
        if (src.x < 0.0 || src.x > 1920.0 || src.y < 0.0 || src.y > 1080.0) return 0.0;
        float distance_signed = src.y-p10title_seam(src.x);
        float distance_cut = side == 0.0 ? abs(distance_signed) : side*distance_signed;
        float ink = texture2D(glyph, src/vec2(1920.0,1080.0)).a;
        if (side != 0.0) ink *= 1.0-step(0.01,distance_cut);
        if (t >= 0.43 || src.y < 420.0) return ink;
        vec2 field_uv = vec2(src.x/1920.0,(src.y-420.0)/660.0);
        vec4 field = texture2D(burn_field,field_uv);
        vec2 cell = floor(vec2(src.x/3.0,(src.y-420.0)/3.0));
        float drift = t*84.0;
        vec2 sample_a = vec2(cell.x+0.5,mod(cell.y+floor(drift),220.0)+0.5)/vec2(640.0,220.0);
        vec2 sample_b = vec2(cell.x+0.5,mod(cell.y+floor(drift)+1.0,220.0)+0.5)/vec2(640.0,220.0);
        vec2 noise = mix(texture2D(burn_field,sample_a).rg,texture2D(burn_field,sample_b).rg,fract(drift));
        float age = t-0.27;
        float strength = t < 0.27 ? p10title_ease(t/0.012) : 1.0-p10title_ease((age-0.025)/0.105);
        float pressure = age > 0.0 && age < 0.105 ? sin(3.14159265*age/0.105) : 0.0;
        float reach = t < 0.27 ? 27.0+8.0*clamp(t/0.27,0.0,1.0) : 35.0+8.0*pressure;
        float outward = side == 0.0 ? 1.0 : p10title_ease((distance_cut+7.0)/4.0);
        float fire = ink*p10title_ease((reach*(0.35+0.76*noise.r)-distance_cut)/4.0)
            *outward*strength*p10title_ease((noise.g-0.30)*8.0);
        if (side != 0.0 && distance_cut <= 0.0) {
            ink *= 1.0-p10title_ease((2.0+3.0*noise.r+distance_cut)/3.0)*strength;
        }
        return ink+fire*(1.0-ink);
    }
""", fragment_300="""
    float p10title_t = max(0.0,u_p10title_time);
    vec2 p10title_dst = v_p10title_uv*vec2(1920.0,1080.0);
    float p10title_alpha;
    if (p10title_t < 0.27) {
        float p10title_q = pow(clamp(p10title_t/0.27,0.0,1.0),3.2);
        vec2 p10title_delta = vec2(620.0,65.0)*(1.0-p10title_q);
        float p10title_a = p10title_piece(tex0,tex1,p10title_dst+p10title_delta,1.0,p10title_t);
        float p10title_b = p10title_piece(tex0,tex1,p10title_dst-p10title_delta,-1.0,p10title_t);
        float p10title_fade = clamp(p10title_t/0.025,0.0,1.0);
        p10title_a *= p10title_fade;
        p10title_b *= p10title_fade;
        p10title_alpha = p10title_a+p10title_b*(1.0-p10title_a);
    } else {
        float p10title_scale = 0.972+0.028*p10title_ease((p10title_t-0.325)/0.105);
        p10title_dst.y = (p10title_dst.y-740.0)/p10title_scale+740.0;
        p10title_alpha = p10title_piece(tex0,tex1,p10title_dst,0.0,p10title_t);
    }
    gl_FragColor = vec4(vec3(p10title_alpha),p10title_alpha);
""")

    renpy.register_shader("ko.p10_spear_title_ink", variables="""
    uniform sampler2D tex0;
    uniform sampler2D tex1;
    uniform float u_p10ink_time;
    uniform float u_p10ink_outro;
    attribute vec2 a_tex_coord;
    varying vec2 v_p10ink_uv;
""", vertex_300="v_p10ink_uv = a_tex_coord;", fragment_functions="""
    float p10ink_ease(float x) {
        x = clamp(x,0.0,1.0);
        return x*x*(3.0-2.0*x);
    }
""", fragment_300="""
    float p10ink_age = max(0.0,u_p10ink_time);
    vec2 p10ink_pixel = v_p10ink_uv*vec2(1920.0,1080.0);
    vec2 p10ink_uv = (p10ink_pixel-vec2(0.0,310.0))/vec2(1280.0,160.0);
    float p10ink_alpha = 0.0;
    if (p10ink_uv.x >= 0.0 && p10ink_uv.x <= 1.0 && p10ink_uv.y >= 0.0 && p10ink_uv.y <= 1.0) {
        vec4 p10ink_field = texture2D(tex1,p10ink_uv);
        float p10ink_p = 1.05;
        if (p10ink_age < 0.075) p10ink_p = 0.035+0.085*pow(clamp(p10ink_age/0.075,0.0,1.0),1.6);
        else if (p10ink_age < 0.285) p10ink_p = 0.12+0.92*pow(clamp((p10ink_age-0.075)/0.21,0.0,1.0),1.18);
        if (u_p10ink_outro > 0.5) p10ink_p = -0.05+1.10*p10ink_ease(p10ink_age/0.35);
        float p10ink_reveal = clamp((p10ink_p-p10ink_field.r)*55.0+0.5,0.0,1.0);
        float p10ink_front = p10ink_ease((1.0-abs(p10ink_p-p10ink_field.r-0.015)/0.13-0.2)*2.0);
        float p10ink_envelope = p10ink_ease((p10ink_age-0.055)/0.045)*(1.0-p10ink_ease((p10ink_age-0.265)/0.075));
        float p10ink_fire = texture2D(tex0,v_p10ink_uv).a*p10ink_front*p10ink_ease((p10ink_field.g-0.43)*9.0)*p10ink_envelope*0.76;
        if (u_p10ink_outro > 0.5) p10ink_reveal = 1.0-p10ink_reveal;
        p10ink_alpha = texture2D(tex0,v_p10ink_uv).a*p10ink_reveal;
        p10ink_alpha += p10ink_fire*(1.0-p10ink_alpha);
        if (u_p10ink_outro > 0.5) p10ink_alpha *= 1.0-0.55*p10ink_ease(p10ink_age/0.35);
    }
    gl_FragColor = vec4(vec3(p10ink_alpha),p10ink_alpha);
""")

init 230 python:
    def ko_p10_spear_title_render(self, width, height, st, at):
        t = max(0.0, self.frame if self.frame is not None else st)
        burn_duration = p10_spear_title_burn_duration()
        burn_complete = 0.48 + burn_duration
        if renpy.is_skipping() or not _preferences.transitions:
            t = max(t, burn_complete)
        lang = p10_spear_title_language()
        result = renpy.Render(1920, 1080)
        if self.outro:
            
            result.blit(renpy.render(_p10title_hanzi,1920,1080,st,at),(0,0))
            outro_duration = p10_spear_title_outro_duration()
            if t < outro_duration:
                if lang == "ja":
                    sub = Transform(_p10title_subs[lang],alpha=1.0-_p10title_ease(t/outro_duration))
                else:
                    sub = Model((1920,1080)).texture(_p10title_subs[lang]).texture(_p10title_fields[lang])
                    sub.shader("ko.p10_spear_title_ink" if _preferences.language == "japanese" else "p10.spear_title_ink").uniform("u_p10ink_time", t*0.35/outro_duration).uniform("u_p10ink_outro", 1.0)
                result.blit(renpy.render(sub,1920,1080,st,at),(0,0))
                if self.frame is None:
                    renpy.redraw(self, 1.0/60.0)
            return result
        age = t-0.27
        if 0.0 < age < 0.13:
            pulse = _p10title_math.sin(_p10title_math.pi*age/0.13)
            veil = Solid((0,0,0,int(255*0.11*pulse/0.90)), xsize=1920, ysize=1080)
            result.blit(renpy.render(veil,1920,1080,st,at),(0,0))
        if t < 0.43:
            title = Model((1920,1080)).texture(_p10title_hanzi).texture(_p10title_edge)
            title.shader("ko.p10_spear_title_clamp" if _preferences.language == "japanese" else "p10.spear_title_clamp").uniform("u_p10title_time", t)
            result.blit(renpy.render(title,1920,1080,st,at),(0,0))
            self._sparks(result,t,st,at)
        else:
            result.blit(renpy.render(_p10title_hanzi,1920,1080,st,at),(0,0))
        if t >= 0.48:
            if t < burn_complete:
                sub = Model((1920,1080)).texture(_p10title_subs[lang]).texture(_p10title_fields[lang])
                sub.shader("ko.p10_spear_title_ink" if _preferences.language == "japanese" else "p10.spear_title_ink").uniform("u_p10ink_time", (t-0.48)*0.35/burn_duration).uniform("u_p10ink_outro", 0.0)
            else:
                sub = _p10title_subs[lang]
            result.blit(renpy.render(sub,1920,1080,st,at),(0,0))
        if self.frame is None and t < burn_complete:
            renpy.redraw(self, 1.0/60.0)
        return result
    
    P10SpearTitle.render = ko_p10_spear_title_render
